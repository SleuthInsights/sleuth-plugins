---
expect:
  project_id: string
  dataset_id: string
---

{
  "id": "d4b81f3e-2c6a-4e0b-8f7d-5a9c3e1b2d01",
  "title": "GLP-1 and incretin obesity pipeline",
  "objective": "Obesity assets acting on GLP-1 and related incretin, amylin, and glucagon pathways, with sponsor, mechanism, route, highest phase, and next catalyst.",
  "status": "complete",
  "version": 1,
  "is_current": true,
  "columns": [
    {
      "id": "asset",
      "name": "asset",
      "description": "Asset name, with brand name when marketed.",
      "type": "string"
    },
    {
      "id": "company",
      "name": "company",
      "description": "Sponsoring company or partnership.",
      "type": "string"
    },
    {
      "id": "mechanism",
      "name": "mechanism",
      "description": "Primary mechanism of action.",
      "type": "categorical"
    },
    {
      "id": "route",
      "name": "route",
      "description": "Route of administration.",
      "type": "categorical"
    },
    {
      "id": "highest_phase",
      "name": "highest_phase",
      "description": "Highest development phase reached for obesity.",
      "type": "categorical"
    },
    {
      "id": "next_catalyst",
      "name": "next_catalyst",
      "description": "Next expected public catalyst.",
      "type": "string"
    }
  ],
  "rows": [
    {
      "id": "row-01",
      "cells": {
        "asset": {
          "value": "Semaglutide (Wegovy)",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "company": {
          "value": "Novo Nordisk",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "mechanism": {
          "value": "GLP-1 RA",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "route": {
          "value": "Subcutaneous",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "highest_phase": {
          "value": "Approved",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "next_catalyst": {
          "value": "Label expansions",
          "confidence_score": 95,
          "cell_type": "fact"
        }
      }
    },
    {
      "id": "row-02",
      "cells": {
        "asset": {
          "value": "Oral semaglutide 25 mg (Wegovy pill)",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "company": {
          "value": "Novo Nordisk",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "mechanism": {
          "value": "GLP-1 RA",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "route": {
          "value": "Oral",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "highest_phase": {
          "value": "Approved",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "next_catalyst": {
          "value": "US launch uptake",
          "confidence_score": 95,
          "cell_type": "fact"
        }
      }
    },
    {
      "id": "row-03",
      "cells": {
        "asset": {
          "value": "Tirzepatide (Zepbound)",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "company": {
          "value": "Eli Lilly",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "mechanism": {
          "value": "GIP/GLP-1 RA",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "route": {
          "value": "Subcutaneous",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "highest_phase": {
          "value": "Approved",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "next_catalyst": {
          "value": "SURMOUNT-MMO outcomes",
          "confidence_score": 95,
          "cell_type": "fact"
        }
      }
    },
    {
      "id": "row-04",
      "cells": {
        "asset": {
          "value": "Orforglipron",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "company": {
          "value": "Eli Lilly",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "mechanism": {
          "value": "Oral small-molecule GLP-1 RA",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "route": {
          "value": "Oral",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "highest_phase": {
          "value": "Filed",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "next_catalyst": {
          "value": "FDA decision",
          "confidence_score": 95,
          "cell_type": "fact"
        }
      }
    },
    {
      "id": "row-05",
      "cells": {
        "asset": {
          "value": "Retatrutide",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "company": {
          "value": "Eli Lilly",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "mechanism": {
          "value": "GIP/GLP-1/glucagon RA",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "route": {
          "value": "Subcutaneous",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "highest_phase": {
          "value": "Phase 3",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "next_catalyst": {
          "value": "TRIUMPH readouts",
          "confidence_score": 95,
          "cell_type": "fact"
        }
      }
    },
    {
      "id": "row-06",
      "cells": {
        "asset": {
          "value": "CagriSema",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "company": {
          "value": "Novo Nordisk",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "mechanism": {
          "value": "Amylin + GLP-1 RA",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "route": {
          "value": "Subcutaneous",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "highest_phase": {
          "value": "Filed",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "next_catalyst": {
          "value": "FDA decision",
          "confidence_score": 95,
          "cell_type": "fact"
        }
      }
    },
    {
      "id": "row-07",
      "cells": {
        "asset": {
          "value": "Amycretin",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "company": {
          "value": "Novo Nordisk",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "mechanism": {
          "value": "Amylin/GLP-1 RA",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "route": {
          "value": "Subcutaneous and oral",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "highest_phase": {
          "value": "Phase 3",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "next_catalyst": {
          "value": "Phase 3 start-up",
          "confidence_score": 95,
          "cell_type": "fact"
        }
      }
    },
    {
      "id": "row-08",
      "cells": {
        "asset": {
          "value": "Survodutide",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "company": {
          "value": "Boehringer Ingelheim",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "mechanism": {
          "value": "Glucagon/GLP-1 RA",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "route": {
          "value": "Subcutaneous",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "highest_phase": {
          "value": "Phase 3",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "next_catalyst": {
          "value": "SYNCHRONIZE readouts",
          "confidence_score": 95,
          "cell_type": "fact"
        }
      }
    },
    {
      "id": "row-09",
      "cells": {
        "asset": {
          "value": "Maridebart cafraglutide (MariTide)",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "company": {
          "value": "Amgen",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "mechanism": {
          "value": "GLP-1 RA / GIPR antagonist",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "route": {
          "value": "Subcutaneous",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "highest_phase": {
          "value": "Phase 3",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "next_catalyst": {
          "value": "MARITIME readouts",
          "confidence_score": 95,
          "cell_type": "fact"
        }
      }
    },
    {
      "id": "row-10",
      "cells": {
        "asset": {
          "value": "Petrelintide",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "company": {
          "value": "Zealand Pharma / Roche",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "mechanism": {
          "value": "Amylin analog",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "route": {
          "value": "Subcutaneous",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "highest_phase": {
          "value": "Phase 2",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "next_catalyst": {
          "value": "Phase 2b data",
          "confidence_score": 95,
          "cell_type": "fact"
        }
      }
    },
    {
      "id": "row-11",
      "cells": {
        "asset": {
          "value": "Mazdutide",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "company": {
          "value": "Innovent",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "mechanism": {
          "value": "Glucagon/GLP-1 RA",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "route": {
          "value": "Subcutaneous",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "highest_phase": {
          "value": "Approved (China)",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "next_catalyst": {
          "value": "Higher-dose data",
          "confidence_score": 95,
          "cell_type": "fact"
        }
      }
    },
    {
      "id": "row-12",
      "cells": {
        "asset": {
          "value": "Ecnoglutide",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "company": {
          "value": "Sciwind Biosciences",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "mechanism": {
          "value": "GLP-1 RA",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "route": {
          "value": "Subcutaneous",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "highest_phase": {
          "value": "Phase 3",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "next_catalyst": {
          "value": "China filing",
          "confidence_score": 95,
          "cell_type": "fact"
        }
      }
    },
    {
      "id": "row-13",
      "cells": {
        "asset": {
          "value": "HRS9531",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "company": {
          "value": "Hengrui / Kailera",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "mechanism": {
          "value": "GIP/GLP-1 RA",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "route": {
          "value": "Subcutaneous",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "highest_phase": {
          "value": "Phase 3",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "next_catalyst": {
          "value": "China Phase 3 data",
          "confidence_score": 95,
          "cell_type": "fact"
        }
      }
    },
    {
      "id": "row-14",
      "cells": {
        "asset": {
          "value": "VK2735",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "company": {
          "value": "Viking Therapeutics",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "mechanism": {
          "value": "GIP/GLP-1 RA",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "route": {
          "value": "Subcutaneous",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "highest_phase": {
          "value": "Phase 3",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "next_catalyst": {
          "value": "VANQUISH readouts",
          "confidence_score": 95,
          "cell_type": "fact"
        }
      }
    },
    {
      "id": "row-15",
      "cells": {
        "asset": {
          "value": "VK2735 oral",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "company": {
          "value": "Viking Therapeutics",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "mechanism": {
          "value": "GIP/GLP-1 RA",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "route": {
          "value": "Oral",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "highest_phase": {
          "value": "Phase 2",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "next_catalyst": {
          "value": "Phase 2 follow-up",
          "confidence_score": 95,
          "cell_type": "fact"
        }
      }
    },
    {
      "id": "row-16",
      "cells": {
        "asset": {
          "value": "Pemvidutide",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "company": {
          "value": "Altimmune",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "mechanism": {
          "value": "Glucagon/GLP-1 RA",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "route": {
          "value": "Subcutaneous",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "highest_phase": {
          "value": "Phase 2",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "next_catalyst": {
          "value": "MASH Phase 2b data",
          "confidence_score": 95,
          "cell_type": "fact"
        }
      }
    },
    {
      "id": "row-17",
      "cells": {
        "asset": {
          "value": "CT-388",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "company": {
          "value": "Roche",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "mechanism": {
          "value": "GIP/GLP-1 RA",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "route": {
          "value": "Subcutaneous",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "highest_phase": {
          "value": "Phase 2",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "next_catalyst": {
          "value": "Phase 2 data",
          "confidence_score": 95,
          "cell_type": "fact"
        }
      }
    },
    {
      "id": "row-18",
      "cells": {
        "asset": {
          "value": "CT-996",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "company": {
          "value": "Roche",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "mechanism": {
          "value": "Oral small-molecule GLP-1 RA",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "route": {
          "value": "Oral",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "highest_phase": {
          "value": "Phase 2",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "next_catalyst": {
          "value": "Phase 2 data",
          "confidence_score": 95,
          "cell_type": "fact"
        }
      }
    },
    {
      "id": "row-19",
      "cells": {
        "asset": {
          "value": "Aleniglipron (GSBR-1290)",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "company": {
          "value": "Structure Therapeutics",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "mechanism": {
          "value": "Oral small-molecule GLP-1 RA",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "route": {
          "value": "Oral",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "highest_phase": {
          "value": "Phase 2",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "next_catalyst": {
          "value": "ACCESS Phase 2b data",
          "confidence_score": 95,
          "cell_type": "fact"
        }
      }
    },
    {
      "id": "row-20",
      "cells": {
        "asset": {
          "value": "Bimagrumab",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "company": {
          "value": "Eli Lilly",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "mechanism": {
          "value": "Activin type II receptor antibody",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "route": {
          "value": "Intravenous",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "highest_phase": {
          "value": "Phase 2",
          "confidence_score": 95,
          "cell_type": "fact"
        },
        "next_catalyst": {
          "value": "Combination data",
          "confidence_score": 95,
          "cell_type": "fact"
        }
      }
    }
  ],
  "total_rows": 24,
  "row_offset": 0,
  "row_limit": 20,
  "updated_at": "2026-09-28T14:02:11.120000"
}
