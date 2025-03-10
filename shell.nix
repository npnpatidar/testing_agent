let pkgs = import <nixpkgs> { };
in pkgs.mkShell {
  LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
    pkgs.stdenv.cc.cc
    pkgs.zlib
    pkgs.libGL
    pkgs.glib
    "/run/opengl-driver"
  ];

  venvDir = ".venv";
  packages = with pkgs;
    [ python312 uv figlet ] ++ (with pkgs.python312Packages; [
      venvShellHook
      pip
      icecream
      python-dotenv
    ]);

  shellHook = ''
    figlet "$(basename "$PWD") env"

    if [ ! -d ".venv" ]; then
      uv venv .venv
    fi

    source .venv/bin/activate

    # alias pip="uv pip"

    uv pip install -r requirements.txt

    figlet "$(basename "$PWD") !!"
  '';
}

