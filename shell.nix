{
  pkgs ? import ./nix/pkgs.nix
}:

pkgs.mkShell {
  name = "pyhon-surveyjs";
  buildInputs = with pkgs; [
      python314
      poetry
  ];
}
