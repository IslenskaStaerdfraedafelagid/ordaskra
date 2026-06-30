#!/usr/bin/bash

# Notkun: ./reps.sh skjal
#
# Finnur öll orð í "skjal" sem koma fyrir
# bæði innan \fl{...} og \sh{...}

file="$1"

# Athuga hvort kallað sé rétt á skriptuna
if [[ -z "$file" || ! -f "$file" ]]; then
  echo "Usage: $0 filename"
  exit 1
fi

# Finnum öll orð sem koma fyrir inn \fl{...}
fl_words=$(grep -oP '\\fl\{\K[^}]+' "$file" | sort -u)

# Finnum öll orð sem koma fyrir inn \sh{...}
sh_words=$(grep -oP '\\sh\{\K[^}]+' "$file" | sort -u)

# Berum saman listana og prentum þau orð sem koma fyrir í báðum
echo "$fl_words" | while read -r w; do
  if echo "$sh_words" | grep -Fxq "$w"; then
    echo "$w"
  fi
done
