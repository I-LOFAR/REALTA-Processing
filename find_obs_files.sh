sudo find /mnt -type f \
  \( -iname "*.fil" -o -iname "*.fil.zst" \) \
  > ./file-list/REALTA-Observation-files.txt 2>/dev/null

