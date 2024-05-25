{
  mkPoetryApplication,
  overrides,
  ...
}:
mkPoetryApplication {
  projectDir = ./.;
  overrides = overrides.withDefaults(self: super: {});
}
