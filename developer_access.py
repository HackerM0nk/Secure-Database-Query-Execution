#!/usr/bin/env python3

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main module
from src.developer_access import main

if __name__ == "__main__":
    main()