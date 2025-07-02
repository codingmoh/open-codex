class OpenCodex < Formula
    desc     "CLI tool to generate shell commands from natural language"
    homepage "https://github.com/codingmoh/open-codex"
    url      "https://github.com/codingmoh/open-codex/releases/download/0.1.17/open-codex-macos.zip"
    sha256   "62852ce7464c630f13d067de964fb180131d399186b109878998ef6096e140a0"
    license  "MIT"
  
    def install
      # Installiere das ganze Verzeichnis in libexec
      libexec.install Dir["*"]    # Erstelle Wrapper-Skript, das das Executable von libexec startet
      (bin/"open-codex").write <<~EOS
        #!/bin/bash
        BREW_PREFIX="$(brew --prefix)"
        exec "$BREW_PREFIX/opt/open-codex/libexec/open-codex" "$@"
        EOS
      chmod "+x", bin/"open-codex"
    end
  end