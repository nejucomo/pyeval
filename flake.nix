{
  description = "pyeval - Conveniently evaluate Python expressions from the shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python3;

        pyeval = python.pkgs.buildPythonPackage {
          pname = "pyeval";
          version = "0.3.0";
          format = "pyproject";

          src = ./.;

          nativeBuildInputs = [
            python.pkgs.setuptools
          ];

          meta = with pkgs.lib; {
            description = "Conveniently evaluate Python expressions from the shell";
            license = licenses.gpl3;
            mainProgram = "pyeval";
          };
        };
      in {
        packages = {
          default = pyeval;
          pyeval = pyeval;
        };

        apps.default = flake-utils.lib.mkApp {
          drv = pyeval;
          name = "pyeval";
        };

        devShells.default = pkgs.mkShell {
          packages = [
            (python.withPackages (ps: with ps; [
              pip
              pytest
              setuptools
            ]))
          ];

          shellHook = ''
            export PYTHONPATH="$PWD/src:$PYTHONPATH"
            echo "pyeval dev shell — run 'pytest src/pyeval/tests' to test"
          '';
        };
      }
    );
}
