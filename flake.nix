{
  description = "Rich Toolkit - Development Environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Python tooling
            python314
            uv

            # Node.js tooling for website
            nodejs_22  # Latest stable Node.js 22.x
            bun        # Bun runtime
          ];

          shellHook = ''
            echo "🚀 Rich Toolkit Development Environment"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "Python version: $(python --version)"
            echo "Node.js version: $(node --version)"
            echo "Bun version: $(bun --version)"
            echo "uv version: $(uv --version)"
          '';
        };
      }
    );
}
