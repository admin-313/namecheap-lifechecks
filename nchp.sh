#!/usr/bin/env bash
set -euo pipefail

# CSV file path; override with: CSV_FILE=/path/to/file.csv ./api_csv.sh ...
CSV="/var/lib/lifechecker/hosts.csv"

HEADER="ApiUser,ApiKey,UserName"

usage() {
  local script_name
  script_name="$(basename "$0")"
  cat <<EOF
Usage:
  $script_name list
  $script_name add <ApiUser> <ApiKey> <UserName>
  $script_name rm (--apiuser <ApiUser> | --username <UserName> | --index <N>)
  [env] CSV_FILE=/path/to/file.csv to use a custom file

Notes:
  - Index in 'list' starts at 1 (data rows only, header not counted).
  - 'add' rejects fields that contain commas or newlines.
  - 'rm' by --index removes the Nth data row as shown by 'list'.
EOF
}

init_csv() {
  if [[ ! -f "$CSV" || ! -s "$CSV" ]]; then
    printf '%s\n' "$HEADER" > "$CSV"
  else
    # Ensure header exists/first line matches; if not, insert it.
    first_line="$(head -n1 "$CSV" || true)"
    if [[ "$first_line" != "$HEADER" ]]; then
      tmp="$(mktemp)"
      printf '%s\n' "$HEADER" > "$tmp"
      # If the first line looks like a header variant, skip duplicating
      tail -n +1 "$CSV" >> "$tmp"
      mv "$tmp" "$CSV"
    fi
  fi
}

has_comma_or_newline() {
  [[ "$1" == *","* ]] && return 0
  [[ "$1" == *$'\n'* ]] && return 0
  return 1
}

list_rows() {
  # Pretty print with index; skip header
  if command -v column >/dev/null 2>&1; then
    # Show a numbered view
    awk 'NR==1{next}{printf "%-4d%s\n", NR-1, $0}' "$CSV" \
      | column -t -s ','
  else
    awk 'NR==1{next}{printf "%-4d%s\n", NR-1, $0}' "$CSV"
  fi
}

add_row() {
  local apiuser="$1" apikey="$2" username="$3"

  # Basic validation
  for v in "$apiuser" "$apikey" "$username"; do
    if has_comma_or_newline "$v"; then
      echo "Error: fields must not contain commas or newlines." >&2
      exit 1
    fi
  done

  # Prevent duplicate ApiUser (adjust if you want different uniqueness)
  if awk -F, -v key="$apiuser" 'NR>1 && $1==key {found=1} END{exit !found}' "$CSV"; then
    echo "Error: ApiUser '$apiuser' already exists." >&2
    exit 1
  fi

    # ✅ Ensure file ends with a newline before appending
  if [[ -s "$CSV" && $(tail -c1 "$CSV" | wc -l) -eq 0 ]]; then
    echo >> "$CSV"
  fi

  printf '%s,%s,%s\n' "$apiuser" "$apikey" "$username" >> "$CSV"
  echo "Added: $apiuser"
}

rm_row() {
  local mode="$1" value="$2"
  local tmp
  tmp="$(mktemp)"

  case "$mode" in
    index)
      # Remove Nth data row (header not counted)
      # Keep header; then print all rows except selected index
      awk -v n="$value" 'BEGIN{n=int(n)} 
        NR==1{print; next}
        {idx=NR-1}
        idx!=n' "$CSV" > "$tmp"
      ;;
    apiuser)
      awk -F, -v key="$value" 'NR==1{print; next} $1!=key' "$CSV" > "$tmp"
      ;;
    username)
      awk -F, -v key="$value" 'NR==1{print; next} $3!=key' "$CSV" > "$tmp"
      ;;
    *)
      echo "Internal error: bad rm mode" >&2
      rm -f "$tmp"; exit 1
      ;;
  esac

  # Detect if anything changed
  if cmp -s "$CSV" "$tmp"; then
    rm -f "$tmp"
    echo "No matching row to remove."
  else
    mv "$tmp" "$CSV"
    echo "Removed."
  fi
}

main() {
  [[ $# -lt 1 ]] && { usage; exit 1; }

  init_csv

  case "$1" in
    list)
      list_rows
      ;;
    add)
      [[ $# -ne 4 ]] && { usage; exit 1; }
      add_row "$2" "$3" "$4"
      ;;
    rm|remove|delete|del)
      shift
      [[ $# -ne 2 ]] && { usage; exit 1; }
      case "$1" in
        --apiuser)   rm_row apiuser "$2" ;;
        --username)  rm_row username "$2" ;;
        --index)     rm_row index "$2" ;;
        *)           usage; exit 1 ;;
      esac
      ;;
    -h|--help|help)
      usage
      ;;
    *)
      usage; exit 1
      ;;
  esac
}

main "$@"

