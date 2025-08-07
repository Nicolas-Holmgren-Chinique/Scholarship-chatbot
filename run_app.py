#!/usr/bin/env python
"""
Simple script to run the Streamlit app
"""
import subprocess
import sys
import os

def main():
    # Set the STREAMLIT_BROWSER_GATHER_USAGE_STATS environment variable to false
    # to skip the email prompt
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    # Run streamlit
    cmd = [
        sys.executable, 
        '-m', 
        'streamlit', 
        'run', 
        'app.py'
    ]
    
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
