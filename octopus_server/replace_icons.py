#!/usr/bin/env python3
"""
Replace FontAwesome icons with Bootstrap Icons in profile_guide.html
"""

# Icon mappings from FontAwesome to Bootstrap Icons
icon_mappings = {
    'fas fa-user-cog': 'bi bi-gear-fill',
    'fas fa-info-circle': 'bi bi-info-circle-fill',
    'fas fa-user-circle': 'bi bi-person-circle',
    'fas fa-chevron-down': 'bi bi-chevron-down',
    'fas fa-user': 'bi bi-person',
    'fas fa-cog': 'bi bi-gear',
    'fas fa-sign-out-alt': 'bi bi-box-arrow-right',
    'fas fa-eye': 'bi bi-eye',
    'fas fa-folder': 'bi bi-folder',
    'fas fa-key': 'bi bi-key',
    'fas fa-plug': 'bi bi-plug',
    'fas fa-bell': 'bi bi-bell',
    'fas fa-tools': 'bi bi-tools',
    'fas fa-plus': 'bi bi-plus',
    'fas fa-edit': 'bi bi-pencil',
    'fas fa-folder-plus': 'bi bi-folder-plus',
    'fas fa-sync': 'bi bi-arrow-clockwise',
    'fas fa-download': 'bi bi-download',
    'fas fa-rocket': 'bi bi-rocket',
    'fas fa-database': 'bi bi-database'
}

# Read the file
file_path = 'c:/Users/aries/PycharmProjects/octopus/octopus_server/pages/profile_guide.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all icons
for fa_icon, bi_icon in icon_mappings.items():
    content = content.replace(fa_icon, bi_icon)

# Write back to file
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Icon replacement complete!")
