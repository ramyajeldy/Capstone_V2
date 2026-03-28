from __future__ import annotations

import math
import re
import time
import socket
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs

import numpy as np
import pandas as pd
import requests
import tldextract
import torch
import torch.nn.functional as F
from datasets import Dataset, load_dataset
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)

try:
    import whois
except Exception:
    whois = None

try:
    import idna
except Exception:
    idna = None

try:
    from confusable_homoglyphs import confusables
except Exception:
    confusables = None


SUSPICIOUS_KEYWORDS = {
    "login", "secure", "verify", "update", "account", "signin", "confirm",
    "password", "wallet", "pay", "payment", "invoice", "alert", "unlock",
    "reset", "limited", "suspended", "support", "bonus", "gift", "free",
    "amazon", "paypal", "microsoft", "apple", "netflix", "office365"
}

SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly", "cutt.ly"
}

TRUSTED_BRANDS = {
    "google.com", "paypal.com", "apple.com", "microsoft.com",
    "amazon.com", "netflix.com", "facebook.com", "instagram.com",
    "dropbox.com", "office.com"
}

DEFAULT_MODEL_NAME = "distilbert-base-uncased"


def normalize_url(url: str) -> str:
    url = str(url or "").strip()
    if not url:
        return ""
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        url = "http://" + url
    return url


def safe_parse_url(url: str) -> Dict[str, Any]:
    url = normalize_url(url)
    try:
        parsed = urlparse(url)
        try:
            hostname = parsed.hostname or ""
        except ValueError:
            hostname = ""

        return {
            "normalized_url": url,
            "parsed": parsed,
            "hostname": hostname,
            "path": parsed.path or "",
            "query": parsed.query or "",
        }
    except Exception:
        return {
            "normalized_url": url,
            "parsed": None,
            "hostname": "",
            "path": "",
            "query": "",
        }


def is_reasonably_parseable(url: str) -> bool:
    try:
        info = safe_parse_url(url)
        return bool(info["normalized_url"])
    except Exception:
        return False


def preprocess_url_for_transformer(url: str) -> str:
    info = safe_parse_url(url)
    return (
        f"url: {info['normalized_url']} [SEP] "
        f"host: {info['hostname']} [SEP] "
        f"path: {info['path']} [SEP] "
        f"query: {info['query']}"
    )


def get_hostname(url: str) -> str:
    info = safe_parse_url(url)
    return info["hostname"]


def get_registered_domain(hostname: str) -> str:
    if not hostname:
        return ""
    ext = tldextract.extract(hostname)
    if not ext.suffix:
        return hostname.lower()
    return f"{ext.domain}.{ext.suffix}".lower()


def has_ip_address(host: str) -> int:
    try:
        socket.inet_aton(host)
        return 1
    except OSError:
        return 0


def shannon_entropy(text: str) -> float:
    if not text:
        return 0.0
    probs = [text.count(c) / len(text) for c in set(text)]
    return -sum(p * math.log2(p) for p in probs if p > 0)


def decode_idna_host(hostname: str) -> Tuple[str, bool]:
    if not hostname or idna is None:
        return hostname, False
    try:
        labels = hostname.split(".")
        decoded_labels = []
        changed = False
        for label in labels:
            if label.startswith("xn--"):
                decoded_labels.append(idna.decode(label))
                changed = True
            else:
                decoded_labels.append(label)
        return ".".join(decoded_labels), changed
    except Exception:
        return hostname, False


class WhoisEnricher:
    def __init__(self, sleep_seconds: float = 0.0):
        self.sleep_seconds = sleep_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}

    def _pick_date(self, value: Any) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, list):
            for item in value:
                if isinstance(item, datetime):
                    value = item
                    break
        if isinstance(value, datetime):
            return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
        return None

    def get_domain_age_days(self, hostname: str) -> Dict[str, int]:
        reg = get_registered_domain(hostname)
        if not reg:
            return {"whois_domain_age_days": -1, "whois_lookup_ok": 0}

        if reg in self.cache:
            return self.cache[reg]

        if whois is None:
            result = {"whois_domain_age_days": -1, "whois_lookup_ok": 0}
            self.cache[reg] = result
            return result

        try:
            time.sleep(self.sleep_seconds)
            info = whois.whois(reg)
            creation_date = getattr(info, "creation_date", None)
            creation_date = self._pick_date(creation_date)

            if creation_date is None:
                result = {"whois_domain_age_days": -1, "whois_lookup_ok": 0}
            else:
                age = max((datetime.now(timezone.utc) - creation_date).days, 0)
                result = {"whois_domain_age_days": int(age), "whois_lookup_ok": 1}
        except Exception:
            result = {"whois_domain_age_days": -1, "whois_lookup_ok": 0}

        self.cache[reg] = result
        return result


class HomographDetector:
    def detect(self, hostname: str) -> Dict[str, Any]:
        decoded, changed = decode_idna_host(hostname)

        scripts = set()
        for ch in decoded:
            if ch.isalpha():
                if ch.isascii():
                    scripts.add("LATIN")
                else:
                    scripts.add("NON_LATIN")

        confusable_flag = 0
        if confusables is not None and decoded:
            try:
                confusable_flag = int(bool(confusables.is_confusable(decoded)))
            except Exception:
                confusable_flag = 0

        decoded_reg = get_registered_domain(decoded)
        brand_collision = 0
        if decoded_reg and decoded_reg not in TRUSTED_BRANDS:
            for brand in TRUSTED_BRANDS:
                if decoded_reg.replace("-", "") == brand.replace("-", ""):
                    brand_collision = 1
                    break

        return {
            "idna_decoded_host": decoded,
            "idna_changed": int(changed),
            "punycode_present": int("xn--" in hostname.lower()),
            "has_non_ascii_host": int(any(ord(c) > 127 for c in decoded)),
            "mixed_script_host": int(len(scripts) > 1),
            "confusable_host": confusable_flag,
            "brand_collision_like": brand_collision,
        }


class OpenPhishIntel:
    def __init__(self, feed_url: str = "https://openphish.com/feed.txt"):
        self.feed_url = feed_url
        self.url_set: set[str] = set()
        self.domain_set: set[str] = set()

    def load_feed(self) -> None:
        self.url_set.clear()
        self.domain_set.clear()
        try:
            response = requests.get(self.feed_url, timeout=10)
            response.raise_for_status()
            lines = [line.strip() for line in response.text.splitlines() if line.strip()]
            for line in lines:
                url = normalize_url(line).lower()
                self.url_set.add(url)
                host = get_hostname(url)
                if host:
                    self.domain_set.add(get_registered_domain(host))
        except Exception:
            pass

    def lookup(self, url: str) -> Dict[str, int]:
        norm = normalize_url(url).lower()
        host = get_hostname(norm)
        reg = get_registered_domain(host) if host else ""
        return {
            "openphish_exact_match": int(norm in self.url_set),
            "openphish_domain_match": int(reg in self.domain_set if reg else 0),
        }


@dataclass
class URLIntelligenceResult:
    url: str
    normalized_url: str
    hostname: str
    registered_domain: str
    transformer_probability: float
    final_probability: float
    prediction: str
    whois_domain_age_days: int
    whois_lookup_ok: int
    openphish_exact_match: int
    openphish_domain_match: int
    punycode_present: int
    idna_changed: int
    has_non_ascii_host: int
    mixed_script_host: int
    confusable_host: int
    reasons: List[str]


class URLFeatureExtractor:
    def __init__(self):
        self.whois_enricher = WhoisEnricher()
        self.homograph = HomographDetector()
        self.openphish = OpenPhishIntel()

    def refresh_openphish(self):
        self.openphish.load_feed()

    def extract_live_features(self, url: str, use_whois: bool = True) -> Dict[str, Any]:
        info = safe_parse_url(url)
        normalized = info["normalized_url"]
        hostname = info["hostname"]
        reg_domain = get_registered_domain(hostname) if hostname else ""
        full_text = normalized.lower()

        try:
            query_keys = parse_qs(info["query"] or "")
        except Exception:
            query_keys = {}

        features: Dict[str, Any] = {
            "normalized_url": normalized,
            "hostname": hostname,
            "registered_domain": reg_domain,
            "url_length": len(normalized),
            "url_entropy": shannon_entropy(normalized),
            "host_is_ip": has_ip_address(hostname) if hostname else 0,
            "subdomain_count": max(len(hostname.split(".")) - 2, 0) if hostname else 0,
            "query_param_count": len(query_keys),
            "shortener_domain": int(reg_domain in SHORTENER_DOMAINS),
            "suspicious_keyword_hits": sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in full_text),
        }

        features.update(self.homograph.detect(hostname))
        features.update(self.openphish.lookup(normalized))

        if use_whois and hostname:
            features.update(self.whois_enricher.get_domain_age_days(hostname))
        else:
            features.update({"whois_domain_age_days": -1, "whois_lookup_ok": 0})

        return features


class URLIntelligenceModel:
    def __init__(self, model_dir: Optional[str] = None, base_model_name: str = DEFAULT_MODEL_NAME):
        self.base_model_name = base_model_name
        self.model_dir = model_dir
        self.tokenizer = None
        self.model = None
        self.extractor = URLFeatureExtractor()

        if model_dir and Path(model_dir).exists():
            self.load_local(model_dir)

    def _preprocess_url_for_transformer(self, url: str) -> str:
        info = safe_parse_url(url)
        hostname = info["hostname"]
        decoded_host, _ = decode_idna_host(hostname)

        parts = [
            f"url: {info['normalized_url']}",
            f"host: {hostname}",
            f"decoded_host: {decoded_host}",
            f"path: {info['path']}",
            f"query: {info['query']}",
        ]
        return " [SEP] ".join(parts)

    def load_local(self, model_dir: str) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        self.model_dir = model_dir

    def prepare_training_dataset(
        self,
        dataset_name: str = "Mitake/PhishingURLsANDBenignURLs",
        text_col: str = "url",
        label_col: str = "label",
        sample_size: Optional[int] = None,
        random_state: int = 42,
    ) -> Tuple[Dataset, Dataset]:
        ds = load_dataset(dataset_name)

        df = ds["train"].to_pandas()[[text_col, label_col]].copy()
        df = df.dropna(subset=[text_col, label_col]).drop_duplicates(subset=[text_col])
        df[text_col] = df[text_col].astype(str)

        df = df[df[text_col].apply(is_reasonably_parseable)].copy()

        if df[label_col].dtype == "object":
            df[label_col] = df[label_col].astype(str).str.strip().str.lower()
            mapping = {
                "benign": 0,
                "legitimate": 0,
                "safe": 0,
                "0": 0,
                "phishing": 1,
                "malicious": 1,
                "1": 1,
            }
            df[label_col] = df[label_col].map(mapping)

        df[label_col] = pd.to_numeric(df[label_col], errors="coerce")
        df = df.dropna(subset=[label_col])
        df[label_col] = df[label_col].astype(int)

        if sample_size and sample_size < len(df):
            df = df.sample(sample_size, random_state=random_state)

        df["text_for_model"] = df[text_col].map(self._preprocess_url_for_transformer)

        train_df = df.sample(frac=0.8, random_state=random_state)
        eval_df = df.drop(train_df.index)

        train_ds = Dataset.from_pandas(
            train_df[["text_for_model", label_col]]
            .rename(columns={"text_for_model": "text", label_col: "label"})
            .reset_index(drop=True)
        )

        eval_ds = Dataset.from_pandas(
            eval_df[["text_for_model", label_col]]
            .rename(columns={"text_for_model": "text", label_col: "label"})
            .reset_index(drop=True)
        )

        return train_ds, eval_ds

    def train(
        self,
        model_dir: str = "bert_url_model",
        dataset_name: str = "Mitake/PhishingURLsANDBenignURLs",
        text_col: str = "url",
        label_col: str = "label",
        sample_size: Optional[int] = 50000,
        random_state: int = 42,
        epochs: int = 1,
        batch_size: int = 8,
        learning_rate: float = 2e-5,
        max_length: int = 256,
    ) -> Dict[str, Any]:
        train_ds, eval_ds = self.prepare_training_dataset(
            dataset_name=dataset_name,
            text_col=text_col,
            label_col=label_col,
            sample_size=sample_size,
            random_state=random_state,
        )

        tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)
        model = AutoModelForSequenceClassification.from_pretrained(self.base_model_name, num_labels=2)

        def tokenize(batch):
            return tokenizer(batch["text"], truncation=True, max_length=max_length)

        train_ds = train_ds.map(tokenize, batched=True)
        eval_ds = eval_ds.map(tokenize, batched=True)

        data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

        def compute_metrics(eval_pred):
            logits, labels = eval_pred
            predictions = np.argmax(logits, axis=-1)
            probs = torch.softmax(torch.tensor(logits), dim=1)[:, 1].numpy()

            precision, recall, f1, _ = precision_recall_fscore_support(
                labels, predictions, average="weighted"
            )
            acc = accuracy_score(labels, predictions)
            auc = roc_auc_score(labels, probs)

            return {
                "accuracy": float(acc),
                "precision": float(precision),
                "recall": float(recall),
                "f1": float(f1),
                "roc_auc": float(auc),
            }

        training_args = TrainingArguments(
            output_dir="./results",
            overwrite_output_dir=True,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            eval_strategy="epoch",
            save_strategy="epoch",
            logging_strategy="steps",
            logging_steps=50,
            load_best_model_at_end=True,
            report_to="none",
            learning_rate=learning_rate,
            seed=random_state,
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_ds,
            eval_dataset=eval_ds,
            tokenizer=tokenizer,
            data_collator=data_collator,
            compute_metrics=compute_metrics,
        )

        trainer.train()
        metrics = trainer.evaluate()

        Path(model_dir).mkdir(parents=True, exist_ok=True)
        trainer.save_model(model_dir)
        tokenizer.save_pretrained(model_dir)

        self.tokenizer = tokenizer
        self.model = trainer.model
        self.model_dir = model_dir

        return metrics

    def bert_url_score(self, url: str) -> float:
        if self.tokenizer is None or self.model is None:
            raise RuntimeError("Model not loaded. Train or load the model first.")

        text = self._preprocess_url_for_transformer(url)
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=256,
        )

        self.model.eval()
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = F.softmax(outputs.logits, dim=1)

        return float(probs[0][1].item())

    def predict_url(
        self,
        url: str,
        threshold: float = 0.5,
        use_whois: bool = True,
    ) -> URLIntelligenceResult:
        features = self.extractor.extract_live_features(url, use_whois=use_whois)
        transformer_probability = self.bert_url_score(url)

        bonus = 0.0
        reasons: List[str] = []

        if features["openphish_exact_match"]:
            bonus += 0.45
            reasons.append("Exact URL match in OpenPhish feed")
        if features["openphish_domain_match"]:
            bonus += 0.20
            reasons.append("Registered domain seen in OpenPhish feed")
        if features["punycode_present"]:
            bonus += 0.12
            reasons.append("Punycode present in hostname")
        if features["confusable_host"]:
            bonus += 0.12
            reasons.append("Hostname contains confusable or homoglyph-like characters")
        if features["mixed_script_host"]:
            bonus += 0.10
            reasons.append("Mixed writing systems detected in hostname")
        if features["suspicious_keyword_hits"] >= 2:
            bonus += 0.10
            reasons.append("Multiple suspicious phishing-related keywords found")
        if features["shortener_domain"]:
            bonus += 0.06
            reasons.append("URL shortener domain used")
        if features["host_is_ip"]:
            bonus += 0.08
            reasons.append("Hostname is an IP address")
        if features["whois_lookup_ok"] and 0 <= features["whois_domain_age_days"] < 60:
            bonus += 0.12
            reasons.append("Very young domain based on WHOIS age")
        if features["brand_collision_like"]:
            bonus += 0.12
            reasons.append("Hostname resembles a trusted brand")

        final_probability = min(
            0.9999,
            max(0.0001, transformer_probability + bonus * (1.0 - transformer_probability))
        )

        if not reasons:
            reasons.append("Prediction driven mainly by transformer-learned URL patterns")

        return URLIntelligenceResult(
            url=url,
            normalized_url=features["normalized_url"],
            hostname=features["hostname"],
            registered_domain=features["registered_domain"],
            transformer_probability=transformer_probability,
            final_probability=final_probability,
            prediction="phishing" if final_probability >= threshold else "benign",
            whois_domain_age_days=int(features["whois_domain_age_days"]),
            whois_lookup_ok=int(features["whois_lookup_ok"]),
            openphish_exact_match=int(features["openphish_exact_match"]),
            openphish_domain_match=int(features["openphish_domain_match"]),
            punycode_present=int(features["punycode_present"]),
            idna_changed=int(features["idna_changed"]),
            has_non_ascii_host=int(features["has_non_ascii_host"]),
            mixed_script_host=int(features["mixed_script_host"]),
            confusable_host=int(features["confusable_host"]),
            reasons=reasons,
        )

    def predict_many(self, urls: List[str], threshold: float = 0.5, use_whois: bool = True) -> pd.DataFrame:
        rows = []
        for url in urls:
            result = self.predict_url(url, threshold=threshold, use_whois=use_whois)
            rows.append({
                "url": result.url,
                "prediction": result.prediction,
                "transformer_probability": round(result.transformer_probability, 4),
                "final_probability": round(result.final_probability, 4),
                "registered_domain": result.registered_domain,
                "domain_age_days": result.whois_domain_age_days,
                "openphish_exact_match": result.openphish_exact_match,
                "openphish_domain_match": result.openphish_domain_match,
                "punycode_present": result.punycode_present,
                "confusable_host": result.confusable_host,
                "reasons": "; ".join(result.reasons),
            })
        return pd.DataFrame(rows)


model = URLIntelligenceModel()

metrics = model.train(
    model_dir="bert_url_model",
    dataset_name="Mitake/PhishingURLsANDBenignURLs",
    text_col="url",
    label_col="label",
    sample_size=50000,
    epochs=1,
    batch_size=8
)

metrics
model = URLIntelligenceModel(model_dir="bert_url_model")
model.extractor.refresh_openphish()
from dataclasses import asdict

result = model.predict_url("http://xn--pple-43d.com/login")
asdict(result)
urls = [
    "https://www.google.com",
    "http://xn--pple-43d.com/login",
    "http://paypal-secure-login.verify-user.com"
]

df_results = model.predict_many(urls)
df_results