#!/bin/bash

# Stateful PyTeal Contract
echo "Deploying Stateful PyTeal..."
echo '{
  "action": "deploy",
  "code": "from pyteal import *\ndef approval(): return Approve()\ndef clear(): return Approve()",
  "contract_type": "stateful",
  "lang": "pyteal"
}' | python3 deploy.py
echo -e "\n------------------------\n"

# Stateless PyTeal Contract
echo "Deploying Stateless PyTeal..."
echo '{
  "action": "deploy",
  "code": "from pyteal import *\ndef logic(): return Approve()",
  "contract_type": "stateless",
  "lang": "pyteal"
}' | python3 deploy.py
echo -e "\n------------------------\n"

# Stateful TEAL Contract
echo "Deploying Stateful TEAL..."
echo '{
  "action": "deploy",
  "code": "#pragma version 6\nint 1\nreturn\n// CLEAR_PROGRAM\n#pragma version 6\nint 1\nreturn",
  "contract_type": "stateful",
  "lang": "teal"
}' | python3 deploy.py
echo -e "\n------------------------\n"

# Stateless TEAL Contract
echo "Deploying Stateless TEAL..."
echo '{
  "action": "deploy",
  "code": "#pragma version 6\nint 1\nreturn",
  "contract_type": "stateless",
  "lang": "teal"
}' | python3 deploy.py
echo -e "\n------------------------\n"
