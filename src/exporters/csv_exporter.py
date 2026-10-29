"""CSV Exporter with formula injection protection and multiple layout options."""

from __future__ import annotations

import csv
import io
from typing import Any, Dict, List, Set, Tuple

from src.database.models import DocumentRecord, ExtractedFieldRecord


class CSVExporter:
    """Exports structured field extractions to sanitized CSV."""

    DANGEROUS_PREFIXES = ("=", "+", "-", "@", "\t", "\r")

    @classmethod
    def sanitize_cell(cls, value: Any) -> str:
        """Sanitize text to prevent CSV/Excel Formula Injection attacks."""
        if value is None:
            return ""
        str_val = str(value)
        if str_val.startswith(cls.DANGEROUS_PREFIXES):
            return f"'{str_val}"
        return str_val

    @classmethod
    def export_long_format(
        cls,
        items: List[Tuple[DocumentRecord, List[ExtractedFieldRecord]]],
        only_verified: bool = False,
        exclude_invalid: bool = False,
    ) -> str:
        """Export in long relational format (one row per extracted field)."""
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")

        headers = [
            "document_id",
            "filename",
            "upload_time",
            "template",
            "processing_status",
            "field_name",
            "extracted_value",
            "normalized_value",
            "data_type",
            "source_page",
            "evidence_excerpt",
            "extraction_method",
            "validation_status",
            "review_status",
            "is_user_corrected",
        ]
        writer.writerow(headers)

        for doc, fields in items:
            for f in fields:
                if only_verified and f.review_status != "verified":
                    continue
                if exclude_invalid and f.validation_status in ("invalid", "missing"):
                    continue

                row = [
                    cls.sanitize_cell(doc.id),
                    cls.sanitize_cell(doc.filename),
                    cls.sanitize_cell(doc.upload_time),
                    cls.sanitize_cell(doc.selected_template),
                    cls.sanitize_cell(doc.processing_status),
                    cls.sanitize_cell(f.field_name),
                    cls.sanitize_cell(f.extracted_value),
                    cls.sanitize_cell(f.normalized_value),
                    cls.sanitize_cell(f.data_type),
                    f.source_page,
                    cls.sanitize_cell(f.evidence_excerpt),
                    cls.sanitize_cell(f.extraction_method),
                    cls.sanitize_cell(f.validation_status),
                    cls.sanitize_cell(f.review_status),
                    f.is_user_corrected,
                ]
                writer.writerow(row)

        return output.getvalue()

    @classmethod
    def export(
        cls,
        items: List[Tuple[DocumentRecord, List[ExtractedFieldRecord]]],
        wide_format: bool = False,
        only_verified: bool = False,
        exclude_invalid: bool = False,
    ) -> str:
        """Export items in either wide or long CSV format."""
        if wide_format:
            return cls.export_wide_format(items, only_verified=only_verified, exclude_invalid=exclude_invalid)
        return cls.export_long_format(items, only_verified=only_verified, exclude_invalid=exclude_invalid)

    @classmethod
    def export_wide_format(
        cls,
        items: List[Tuple[DocumentRecord, List[ExtractedFieldRecord]]],
        only_verified: bool = False,
        exclude_invalid: bool = False,
    ) -> str:
        """Export in wide format (one row per document with columns for each field)."""
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")

        # Gather all distinct field names
        all_field_names: Set[str] = set()
        for _, fields in items:
            for f in fields:
                if only_verified and f.review_status != "verified":
                    continue
                if exclude_invalid and f.validation_status in ("invalid", "missing"):
                    continue
                all_field_names.add(f.field_name)

        sorted_fields = sorted(list(all_field_names))

        headers = ["document_id", "filename", "upload_time", "template", "status"] + sorted_fields
        writer.writerow(headers)

        for doc, fields in items:
            field_map: Dict[str, str] = {}
            for f in fields:
                if only_verified and f.review_status != "verified":
                    continue
                if exclude_invalid and f.validation_status in ("invalid", "missing"):
                    continue
                # Prefer normalized value, fall back to extracted value
                val = f.normalized_value if f.normalized_value else (f.extracted_value or "")
                field_map[f.field_name] = val

            row = [
                cls.sanitize_cell(doc.id),
                cls.sanitize_cell(doc.filename),
                cls.sanitize_cell(doc.upload_time),
                cls.sanitize_cell(doc.selected_template),
                cls.sanitize_cell(doc.processing_status),
            ]
            for fn in sorted_fields:
                row.append(cls.sanitize_cell(field_map.get(fn, "")))

            writer.writerow(row)

        return output.getvalue()
