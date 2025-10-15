# aurum-windows-gaming:26100.2192
FROM mcr.microsoft.com/windows/servercore:ltsc2025-amd64
COPY --from=aurum-cache [/phi-codec.dll, /omega.sys, /ao-ledger.dll] C:\
RUN dism /online /add-package /packagepath:C:\windows11.0-kb5055942-x64.cab
COPY harden.ps1 C:\
RUN powershell -ExecutionPolicy Bypass -File C:\harden.ps1
RUN reg add HKLM\SOFTWARE\Aurum /v OmegaTarget /t REG_SZ /d 0.618
EXPOSE 3074/udp 443/tcp 50000-50100/udp
ENTRYPOINT ["C:\\aletheia-gaming.exe"]