export HOME=/tmp
export CARGO_HOME=/tmp/cargo
export RUSTUP_HOME=/tmp/rustup

export PIP_PREFER_BINARY=1

pip install --upgrade pip setuptools wheel
pip install --no-cache-dir -r requirements2.txt
