"""Default starter extraction templates for recurring PDF document categories."""

from typing import Any, Dict, List

DEFAULT_TEMPLATES: List[Dict[str, Any]] = [
    {
        "name": "General Form",
        "description": "General purpose extraction for standard forms, contact sheets, and administrative records.",
        "category": "General",
        "rules": {
            "fields": {
                "person_name": {
                    "aliases": ["name", "full name", "contact name", "individual"],
                    "data_type": "string",
                    "required": True,
                },
                "email": {
                    "aliases": ["email", "e-mail", "email address", "contact email"],
                    "data_type": "email",
                    "required": False,
                },
                "phone": {
                    "aliases": ["phone", "phone number", "telephone", "mobile", "cell"],
                    "data_type": "phone",
                    "required": False,
                },
                "date": {
                    "aliases": ["date", "submission date", "record date", "dated"],
                    "data_type": "date",
                    "required": False,
                },
                "organization": {
                    "aliases": ["organization", "company", "institution", "agency"],
                    "data_type": "string",
                    "required": False,
                },
                "address": {
                    "aliases": ["address", "mailing address", "location", "residence"],
                    "data_type": "string",
                    "required": False,
                },
            }
        },
    },
    {
        "name": "Invoices & Receipts",
        "description": "Tailored for billing invoices, commercial receipts, purchase orders, and payment vouchers.",
        "category": "Finance",
        "rules": {
            "fields": {
                "invoice_number": {
                    "aliases": ["invoice number", "invoice #", "inv no", "inv #", "bill no", "receipt #"],
                    "data_type": "string",
                    "required": True,
                },
                "date": {
                    "aliases": ["invoice date", "bill date", "date of issue", "dated", "date"],
                    "data_type": "date",
                    "required": True,
                },
                "organization": {
                    "aliases": ["vendor", "vendor name", "company", "from", "service provider", "biller"],
                    "data_type": "string",
                    "required": True,
                },
                "person_name": {
                    "aliases": ["bill to", "customer name", "client", "billed to", "recipient"],
                    "data_type": "string",
                    "required": False,
                },
                "total_amount": {
                    "aliases": ["total", "total amount", "grand total", "net amount", "balance due", "amount due"],
                    "data_type": "monetary",
                    "required": True,
                },
                "email": {
                    "aliases": ["email", "billing email", "contact email", "support email"],
                    "data_type": "email",
                    "required": False,
                },
                "phone": {
                    "aliases": ["phone", "telephone", "vendor phone", "billing phone"],
                    "data_type": "phone",
                    "required": False,
                },
            }
        },
    },
    {
        "name": "Application & Registration",
        "description": "Optimized for job applications, university registrations, event sign-ups, and membership forms.",
        "category": "Applications",
        "rules": {
            "fields": {
                "person_name": {
                    "aliases": ["applicant name", "full name", "candidate name", "member name", "registrant"],
                    "data_type": "string",
                    "required": True,
                },
                "email": {
                    "aliases": ["email", "applicant email", "contact email"],
                    "data_type": "email",
                    "required": True,
                },
                "phone": {
                    "aliases": ["phone", "mobile", "contact no", "telephone"],
                    "data_type": "phone",
                    "required": True,
                },
                "date": {
                    "aliases": ["application date", "date of birth", "registration date", "submission date", "date"],
                    "data_type": "date",
                    "required": False,
                },
                "organization": {
                    "aliases": ["institution", "university", "college", "current employer", "organization"],
                    "data_type": "string",
                    "required": False,
                },
                "address": {
                    "aliases": ["permanent address", "residential address", "current address", "address"],
                    "data_type": "string",
                    "required": False,
                },
                "application_id": {
                    "aliases": ["application id", "ref no", "applicant id", "registration id", "reg #"],
                    "data_type": "string",
                    "required": False,
                },
            }
        },
    },
    {
        "name": "Business Contracts",
        "description": "Structured extraction for service agreements, nondisclosure agreements, and vendor contracts.",
        "category": "Legal & Business",
        "rules": {
            "fields": {
                "organization": {
                    "aliases": ["party a", "company", "client", "first party", "service provider"],
                    "data_type": "string",
                    "required": True,
                },
                "person_name": {
                    "aliases": ["party b", "contractor", "representative", "second party", "signatory"],
                    "data_type": "string",
                    "required": True,
                },
                "date": {
                    "aliases": ["effective date", "agreement date", "execution date", "commencement date", "dated"],
                    "data_type": "date",
                    "required": True,
                },
                "total_amount": {
                    "aliases": ["contract value", "consideration", "fee", "total compensation", "retainer"],
                    "data_type": "monetary",
                    "required": False,
                },
                "address": {
                    "aliases": ["principal place of business", "registered office", "notice address", "jurisdiction"],
                    "data_type": "string",
                    "required": False,
                },
            }
        },
    },
]
