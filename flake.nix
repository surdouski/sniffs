{
  description = "sniffs MQTT routing";

  inputs.flake-utils.url = "github:numtide/flake-utils";
#  inputs.nixpkgs.url = "github:NixOS/nixpkgs/release-23.05";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.poetry2nix = {
    url = "github:nix-community/poetry2nix";
    inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    poetry2nix,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      inherit (import poetry2nix { inherit pkgs; }) mkPoetryApplication overrides;
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      packages = rec {
        plantdb-message-handler = pkgs.callPackage ./. {
          inherit mkPoetryApplication overrides;
        };
        default = self.packages.${system}.sniffs;
      };

      devShells.default = pkgs.mkShell {
        packages = [poetry2nix.packages.${system}.poetry];
      };
    });
}
