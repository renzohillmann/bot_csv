#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

class DefaultConfig:
    """ Bot Configuration """

    # Bot Framework settings from App Settings or environment
    PORT = int(os.environ.get("PORT", 3978))
    
    # Support for both Azure App Settings and local environment
    # These property names are specifically required by Bot Framework
    @property
    def microsoft_app_id(self):
        return os.environ.get("MicrosoftAppId", "")
        
    @property
    def microsoft_app_password(self):
        return os.environ.get("MicrosoftAppPassword", "")
        
    @property
    def microsoft_app_type(self):
        return os.environ.get("MicrosoftAppType", "SingleTenant")
        
    @property
    def microsoft_app_tenant_id(self):
        return os.environ.get("MicrosoftAppTenantId", "")
    
    # For backward compatibility with your existing code
    APP_ID = microsoft_app_id
    APP_PASSWORD = microsoft_app_password
    APP_TYPE = microsoft_app_type
    APP_TENANTID = microsoft_app_tenant_id