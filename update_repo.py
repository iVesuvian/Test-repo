#!/usr/bin/env python3
import json
import os
import zipfile
import plistlib
from datetime import datetime
import hashlib

REPO_JSON = "repo.json"
IPA_DIRECTORY = "/ipas"
BASE_URL = "https://your-domain.com/apps"

def get_ipa_info(ipa_path):
    """Extract info from IPA file"""
    with zipfile.ZipFile(ipa_path, 'r') as zip_ref:
        # Find Info.plist
        for file in zip_ref.namelist():
            if file.endswith('Info.plist') and 'Payload' in file:
                with zip_ref.open(file) as plist_file:
                    plist = plistlib.load(plist_file)
                    return {
                        'name': plist.get('CFBundleDisplayName', plist.get('CFBundleName')),
                        'bundleIdentifier': plist.get('CFBundleIdentifier'),
                        'version': plist.get('CFBundleShortVersionString'),
                        'minOSVersion': plist.get('MinimumOSVersion', '14.0')
                    }
    return None

def get_file_size(file_path):
    """Get file size in bytes"""
    return os.path.getsize(file_path)

def update_repo():
    """Scan IPA directory and update repo.json"""
    
    # Load existing repo or create new
    if os.path.exists(REPO_JSON):
        with open(REPO_JSON, 'r') as f:
            repo = json.load(f)
    else:
        repo = {
            "name": "My IPA Repository",
            "identifier": "com.yourname.repo",
            "apps": []
        }
    
    # Scan IPA files
    if not os.path.exists(IPA_DIRECTORY):
        os.makedirs(IPA_DIRECTORY)
        return
    
    for filename in os.listdir(IPA_DIRECTORY):
        if not filename.endswith('.ipa'):
            continue
        
        ipa_path = os.path.join(IPA_DIRECTORY, filename)
        ipa_info = get_ipa_info(ipa_path)
        
        if not ipa_info:
            continue
        
        # Find or create app entry
        app_entry = None
        for app in repo['apps']:
            if app['bundleIdentifier'] == ipa_info['bundleIdentifier']:
                app_entry = app
                break
        
        if not app_entry:
            app_entry = {
                "name": ipa_info['name'],
                "bundleIdentifier": ipa_info['bundleIdentifier'],
                "developerName": "Your Name",
                "versions": []
            }
            repo['apps'].append(app_entry)
        
        # Check if version already exists
        version_exists = any(
            v['version'] == ipa_info['version'] 
            for v in app_entry['versions']
        )
        
        if not version_exists:
            version_entry = {
                "version": ipa_info['version'],
                "date": datetime.now().strftime("%Y-%m-%d"),
                "downloadURL": f"{BASE_URL}/{filename}",
                "size": get_file_size(ipa_path),
                "minOSVersion": ipa_info['minOSVersion']
            }
            app_entry['versions'].insert(0, version_entry)
            print(f"Added {ipa_info['name']} v{ipa_info['version']}")
    
    # Save updated repo
    with open(REPO_JSON, 'w') as f:
        json.dump(repo, f, indent=2)
    
    print(f"Repository updated: {REPO_JSON}")

if __name__ == "__main__":
    update_repo()
