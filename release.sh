pyinstaller --clean --onedir \
    --paths src \
    --name open-codex \
    --add-data "src/open_codex/resources:open_codex/resources" \
    --add-binary ".venv/lib/python3.11/site-packages/llama_cpp/lib/libllama.dylib:llama_cpp/lib" \
    --add-binary ".venv/lib/python3.11/site-packages/lib/libggml.dylib:llama_cpp/lib" \
    --add-binary ".venv/lib/python3.11/site-packages/lib/libggml-metal.dylib:llama_cpp/lib" \
    --add-binary ".venv/lib/python3.11/site-packages/lib/libggml-base.dylib:llama_cpp/lib" \
    --add-binary ".venv/lib/python3.11/site-packages/lib/libggml-blas.dylib:llama_cpp/lib" \
    --add-binary ".venv/lib/python3.11/site-packages/lib/libggml-cpu.dylib:llama_cpp/lib" \
    src/open_codex/main.py


cd dist/
zip -r ../open-codex-macos.zip open-codex
cd ..
shasum -a 256 open-codex-macos.zip           

cd dist/open-codex
zip -r ../open-codex-macos.zip open-codex _internal



