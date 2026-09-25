#!/usr/bin/env bash
# Configura la firma crittografica delle commit con chiave SSH.
# Da eseguire una volta sola, sulla macchina da cui scrivi.
set -euo pipefail

CHIAVE="${1:-$HOME/.ssh/id_ed25519.pub}"

if [ ! -f "$CHIAVE" ]; then
  echo "Chiave non trovata: $CHIAVE"
  echo "Generane una con:"
  echo "  ssh-keygen -t ed25519 -C \"tua@email.it\""
  exit 1
fi

git config --global gpg.format ssh
git config --global user.signingkey "$CHIAVE"
git config --global commit.gpgsign true
git config --global tag.gpgsign true

# File di allowed signers: serve a git per verificare in locale.
EMAIL="$(git config --global user.email)"
mkdir -p "$HOME/.config/git"
echo "$EMAIL namespaces=\"git\" $(cat "$CHIAVE")" \
  >> "$HOME/.config/git/allowed_signers"
git config --global gpg.ssh.allowedSignersFile "$HOME/.config/git/allowed_signers"

echo "Firma configurata con $CHIAVE"
echo
echo "Ultimo passo, a mano su GitHub:"
echo "  Settings > SSH and GPG keys > New SSH key"
echo "  Key type: Signing Key   (NON Authentication Key)"
echo "  Incolla questo:"
echo
cat "$CHIAVE"
