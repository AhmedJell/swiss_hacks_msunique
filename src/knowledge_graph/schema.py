from typing import Literal


class SchemaValidationClass:
    triplets = [
        ("COMPANY", "EMPLOYS", "PERSON"),
        ("COMPANY", "OFFERS", "PRODUCT"),
        ("COMPANY", "OPERATES_IN", "INDUSTRY"),
        ("COMPANY", "COMPETES_WITH", "COMPANY"),
        ("COMPANY", "MANAGES", "ASSET"),
        ("COMPANY", "PROVIDES", "SERVICE"),
        ("COMPANY", "DEFINES", "KEY_PERFORMANCE_INDICATOR"),
        ("COMPANY", "HAS_PRESENCE_IN", "REGION"),
        ("COMPANY", "PUBLISHES", "ANNUAL_REPORT"),
        ("COMPANY", "DEALS_IN", "CURRENCY"),
        ("COMPANY", "ORGANIZES", "EVENT"),
        ("COMPANY", "DEVELOPS", "STRATEGY"),
        ("COMPANY", "IDENTIFIES", "RISK"),
        ("SECTOR", "COMPRISES", "INDUSTRY"),
        ("SECTOR", "INFLUENCES", "STRATEGY"),
        ("SECTOR", "IS_ASSOCIATED_WITH", "RISK"),
        ("INDUSTRY", "INCLUDES", "COMPANIES"),
        ("INDUSTRY", "AFFECTS", "STRATEGY"),
        ("INDUSTRY", "FACES", "RISK"),
        ("ANNUAL_REPORT", "INCLUDES", "KEY_PERFORMANCE_INDICATOR"),
        ("ANNUAL_REPORT", "LISTS", "ASSETS"),
        ("ANNUAL_REPORT", "MENTIONS", "CURRENCY"),
        ("ANNUAL_REPORT", "COVERS", "REGION"),
        ("ANNUAL_REPORT", "DESCRIBES", "EVENT"),
        ("ANNUAL_REPORT", "INVOLVES", "PERSON"),
        ("ANNUAL_REPORT", "HIGHLIGHTS", "PRODUCT"),
        ("ANNUAL_REPORT", "DETAILS", "SERVICE"),
        ("ANNUAL_REPORT", "OUTLINES", "STRATEGY"),
        ("ANNUAL_REPORT", "ASSESSES", "RISK"),
        ("KEY_PERFORMANCE_INDICATOR", "HAS_COMPANY", "COMPANY"),
        ("KEY_PERFORMANCE_INDICATOR", "HAS_VALUE", "VALUE"),
        ("KEY_PERFORMANCE_INDICATOR", "HAS_YEAR", "VALUE"),
        ("VALUE", "HAS_YEAR", "YEAR"),
        ("KEY_PERFORMANCE_INDICATOR", "REPORTED_IN", "ANNUAL_REPORT"),
        ("KEY_PERFORMANCE_INDICATOR", "INFLUENCES", "STRATEGY"),
        ("KEY_PERFORMANCE_INDICATOR", "ASSOCIATED_WITH", "RISK"),
        ("ASSET", "OWNED_BY", "COMPANY"),
        ("ASSET", "LISTED_IN", "ANNUAL_REPORT"),
        ("ASSET", "VALUED_IN", "CURRENCY"),
        ("ASSET", "LOCATED_IN", "REGION"),
        ("ASSET", "IMPACTED_BY", "EVENT"),
        ("CURRENCY", "USED_BY", "COMPANY"),
        ("CURRENCY", "MENTIONED_IN", "ANNUAL_REPORT"),
        ("REGION", "INCLUDE_COMPANIES", "COMPANIES"),
        ("REGION", "COVERED_IN", "ANNUAL_REPORT"),
        ("REGION", "HOST_EVENT", "EVENT"),
        ("REGION", "HOME_TO", "PERSON"),
        ("REGION", "MARKET_FOR", "PRODUCT"),
        ("REGION", "DEMANDS", "SERVICE"),
        ("EVENT", "ORGANIZED_BY", "COMPANY"),
        ("EVENT", "LISTED_IN", "ANNUAL_REPORT"),
        ("EVENT", "AFFECTS", "STRATEGY"),
        ("EVENT", "INVOLVES", "PERSON"),
        ("EVENT", "IMPACTS", "PRODUCT"),
        ("EVENT", "INFLUENCES", "SERVICE"),
        ("EVENT", "CONNECTED_TO", "RISK"),
        ("PERSON", "EMPLOYED_BY", "COMPANY"),
        ("PERSON", "MENTIONED_IN", "ANNUAL_REPORT"),
        ("PERSON", "PARTICIPATES_IN", "EVENT"),
        ("PERSON", "CONSUMES", "PRODUCT"),
        ("PERSON", "USES", "SERVICE"),
        ("PERSON", "DEVISES", "STRATEGY"),
        ("PERSON", "ASSESSES", "RISK"),
        ("PRODUCT", "OFFERED_BY", "COMPANY"),
        ("PRODUCT", "LISTED_IN", "ANNUAL_REPORT"),
        ("PRODUCT", "SHOWCASED_AT", "EVENT"),
        ("PRODUCT", "CONSUMED_BY", "PERSON"),
        ("PRODUCT", "INFLUENCED_BY", "STRATEGY"),
        ("PRODUCT", "ASSOCIATED_WITH", "RISK"),
        ("SERVICE", "PROVIDED_BY", "COMPANY"),
        ("SERVICE", "LISTED_IN", "ANNUAL_REPORT"),
        ("SERVICE", "SHOWCASED_AT", "EVENT"),
        ("SERVICE", "USED_BY", "PERSON"),
        ("SERVICE", "INFLUENCED_BY", "STRATEGY"),
        ("SERVICE", "ASSOCIATED_WITH", "RISK"),
        ("STRATEGY", "DEVELOPED_BY", "COMPANY"),
        ("STRATEGY", "OUTLINED_IN", "ANNUAL_REPORT"),
        ("STRATEGY", "INFLUENCED_BY", "KEY_PERFORMANCE_INDICATOR"),
        ("STRATEGY", "SHAPED_BY", "INDUSTRY"),
        ("STRATEGY", "AFFECTED_BY", "SECTOR"),
        ("STRATEGY", "CONSIDERS", "RISK"),
        ("STRATEGY", "RESPONDS_TO", "EVENT"),
        ("RISK", "IDENTIFIED_BY", "COMPANY"),
        ("RISK", "DETAILED_IN", "ANNUAL_REPORT"),
        ("RISK", "INFLUENCED_BY", "KEY_PERFORMANCE_INDICATOR"),
        ("RISK", "FACED_BY", "INDUSTRY"),
        ("RISK", "ASSOCIATED_WITH", "SECTOR"),
        ("RISK", "MITIGATED_BY", "STRATEGY"),
        ("RISK", "ARISING_FROM", "STRATEGY"),
        ("RISK", "ARISING_FROM", "EVENT"),
    ]

    def __init__(self, parent, edge, child):
        if (parent, edge, child) not in self.triplets:
            raise ValueError

    @classmethod
    def entities(cls):
        return set([x for x, _, _ in cls.triplets] + [x for _, _, x in cls.triplets])

    @classmethod
    def relations(cls):
        return set([x for _, x, _ in cls.triplets])

    @classmethod
    def schema(cls):
        return {x: [y for z, y, _ in cls.triplets if z == x] for x in cls.entities()}
    
    
entities = Literal[*SchemaValidationClass.entities()]
relations = Literal[*SchemaValidationClass.relations()]

validation_schema = SchemaValidationClass.triplets