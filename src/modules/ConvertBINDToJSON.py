# ConvertBINDToJSON.py
import dns.zone
import dns.rdataclass
import dns.rdatatype
from dns.exception import DNSException

class ConvertBINDToJSON:
    def convert_record(self, name, rdataset):
        records = []
        for rdata in rdataset:
            record_type = dns.rdatatype.to_text(rdataset.rdtype)
            record = {
                "name": str(name),
                "ttl": rdataset.ttl,
                "type": record_type
            }

            # Mapping record to corresponding handling functions
            conversion_method = getattr(self, f"_convert_{record_type.lower()}", None)
            if conversion_method:
                converted_record = conversion_method(record, rdata)
            else:
                converted_record = self._default_convert(record, rdata)

            if converted_record:
                # Always remove 'rdcomment' if present
                if "rdcomment" in converted_record:
                    del converted_record["rdcomment"]
                records.append(converted_record)

        return records

    # Handling SOA Record
    def _convert_soa(self, record, rdata):
        record["name"] = str(rdata.mname)
        record["admin"] = str(rdata.rname).replace("\\.", ".")
        record["serial"] = rdata.serial
        record["refresh"] = rdata.refresh
        record["retry"] = rdata.retry
        record["expire"] = rdata.expire
        record["minimum"] = rdata.minimum
        record["ttl"] = record.get("ttl", 3600)

        return record

    # Handling NS Record
    def _convert_ns(self, record, rdata):
        record["value"] = str(rdata.target)
        return record

    # Handling CNAME Record
    def _convert_cname(self, record, rdata):
        record["value"] = str(rdata.target)
        return record

    # Handling A Record
    def _convert_a(self, record, rdata):
        record["value"] = rdata.address
        return record

    # Handling AAAA Record
    def _convert_aaaa(self, record, rdata):
        record["value"] = rdata.address
        return record

    # Default handling for other records
    def _default_convert(self, record, rdata):
        rdata_attributes = [attr for attr in dir(rdata) if not attr.startswith("_") and not callable(getattr(rdata, attr))]
        for attr_name in rdata_attributes:
            if attr_name not in ["rdclass", "rdtype"]:
                value = getattr(rdata, attr_name)
                if isinstance(value, bytes):
                    value = value.decode('utf-8')
                record[attr_name] = int(value) if isinstance(value, str) and value.isdigit() else str(value)

        return record
