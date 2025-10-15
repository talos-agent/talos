# Harden the Windows-on-Aurum container for gaming

# Disable HVCI for GPU-passthrough
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\DeviceGuard" -Name "EnableVirtualizationBasedSecurity" -Value 0

# Disable CET shadow-stack
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" -Name "CetShadowStack" -Value 0

# Enable QUIC v3 system-wide
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\HTTP\Parameters" -Name "EnableQuic" -Value 1

# Activate H.265 HVCI offload
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows Media Foundation\Platform" -Name "EnableHardwareAcceleration" -Value 1