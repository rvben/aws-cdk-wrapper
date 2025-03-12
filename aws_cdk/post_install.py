"""
Post-installation script for AWS CDK Python wrapper with bundled Node.js.

This script is executed after the Python package is installed.
It extracts the bundled Node.js binaries and installs the AWS CDK.
"""

import os
import sys
import logging
import platform
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

def create_license_notices():
    """
    Create license notice files in the installation directory.
    This ensures license texts are available even if they weren't included in the distribution.
    """
    try:
        from aws_cdk import PACKAGE_DIR, LICENSES
        
        # AWS CDK License - Apache 2.0
        cdk_license_path = LICENSES.get("aws_cdk")
        if not os.path.exists(cdk_license_path):
            cdk_license_dir = os.path.dirname(cdk_license_path)
            os.makedirs(cdk_license_dir, exist_ok=True)
            
            with open(cdk_license_path, 'w', encoding='utf-8') as f:
                f.write("""
                    Apache License
                    Version 2.0, January 2004
                    http://www.apache.org/licenses/
                    
                    Copyright (c) Amazon.com, Inc. or its affiliates. All Rights Reserved.
                    
                    Licensed under the Apache License, Version 2.0 (the "License");
                    you may not use this file except in compliance with the License.
                    You may obtain a copy of the License at
                    
                        http://www.apache.org/licenses/LICENSE-2.0
                    
                    Unless required by applicable law or agreed to in writing, software
                    distributed under the License is distributed on an "AS IS" BASIS,
                    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
                    See the License for the specific language governing permissions and
                    limitations under the License.
                """.strip())
        
        # Node.js License - MIT
        node_license_path = LICENSES.get("node")
        if not os.path.exists(node_license_path):
            node_license_dir = os.path.dirname(node_license_path)
            os.makedirs(node_license_dir, exist_ok=True)
            
            with open(node_license_path, 'w', encoding='utf-8') as f:
                f.write("""
                    The MIT License
                    
                    Copyright Node.js contributors. All rights reserved.
                    
                    Permission is hereby granted, free of charge, to any person obtaining a copy
                    of this software and associated documentation files (the "Software"), to
                    deal in the Software without restriction, including without limitation the
                    rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
                    sell copies of the Software, and to permit persons to whom the Software is
                    furnished to do so, subject to the following conditions:
                    
                    The above copyright notice and this permission notice shall be included in
                    all copies or substantial portions of the Software.
                    
                    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
                    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
                    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
                    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
                    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
                    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
                    IN THE SOFTWARE.
                """.strip())
    except Exception as e:
        logger.warning(f"Failed to create license notices: {e}")

def main():
    """
    Main function for post-installation.
    Extracts Node.js binaries and installs AWS CDK.
    """
    # Add the package to the Python path so we can import it
    package_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(package_dir))
    
    try:
        from aws_cdk.installer import download_node, install_cdk
        from aws_cdk import is_node_installed, is_cdk_installed, SYSTEM, MACHINE
        
        # Check if offline mode is requested
        offline_mode = os.environ.get("AWS_CDK_OFFLINE") == "1"
        if offline_mode:
            logger.info("Running in offline mode. Using cached binaries if available.")
        
        # Check if we're on a supported platform
        if SYSTEM not in ["windows", "darwin", "linux"]:
            logger.warning(
                f"Unsupported operating system: {SYSTEM}. "
                "The AWS CDK wrapper may not work correctly."
            )
        
        if MACHINE not in ["x86_64", "arm64", "aarch64"]:
            logger.warning(
                f"Unsupported architecture: {MACHINE}. "
                "The AWS CDK wrapper may not work correctly."
            )
        
        # Install Node.js if not already installed
        if not is_node_installed():
            logger.info("Installing Node.js binaries...")
            
            # Try up to 3 times to handle transient network issues
            success = False
            for attempt in range(3):
                if attempt > 0:
                    logger.info(f"Retrying Node.js installation (attempt {attempt+1}/3)...")
                
                if download_node():
                    success = True
                    break
                
                # Don't retry in offline mode
                if offline_mode:
                    break
            
            if not success:
                logger.error(
                    "Failed to install Node.js binaries. "
                    "The AWS CDK wrapper may not work correctly."
                )
                return 1
        
        # Install AWS CDK if not already installed
        if not is_cdk_installed():
            logger.info("Installing AWS CDK...")
            
            # Try up to 3 times to handle transient network issues
            success = False
            for attempt in range(3):
                if attempt > 0:
                    logger.info(f"Retrying AWS CDK installation (attempt {attempt+1}/3)...")
                
                if install_cdk():
                    success = True
                    break
                
                # Don't retry in offline mode
                if offline_mode:
                    break
            
            if not success:
                logger.error(
                    "Failed to install AWS CDK. "
                    "You can try installing it manually by running: "
                    "python -m aws_cdk.installer"
                )
                return 1
        
        # Create license notices if they don't exist
        create_license_notices()
        
        logger.info("AWS CDK Python wrapper successfully installed.")
        return 0
    except Exception as e:
        logger.error(f"Error during post-installation: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 