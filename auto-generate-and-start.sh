#!/usr/bin/env bash
line_break () {
  printf "===================================================================\n"
}

printf "\nAuto generate and apply PIA Wireguard tunnel\n"
line_break

printf "\nGenerating the config... (ensure your PIA cred env vars are set)\n"
line_break
./generate-config.py -s "US West"
sudo mv PIA-US-West* /etc/wireguard/PIA.conf

printf "\nStarting up the WG interface with the new config\n"
line_break
sudo wg-quick up PIA

printf "\nQuick ping test to Google.com to test DNS and tunnel health\n"
line_break
ping -c 2 google.com

printf "\nOpening IP Leak in default browser, ensure it shows US West and nothing leaking\n"
line_break
xdg-open https://ipleak.net/