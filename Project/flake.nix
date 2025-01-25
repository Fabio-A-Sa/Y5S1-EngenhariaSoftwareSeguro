{
  description = "A flake for the ESS project";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = { nixpkgs, ... }: 
    let 
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
      };
      
    in {
      devShell.${system} = pkgs.mkShell {
        packages = with pkgs; [
          python3
          openssl
          sqlite
        ];

        shellHook = ''
          source .venv/bin/activate
        '';
      };
    };
}
