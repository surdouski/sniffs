{
  mkPoetryApplication,
  ...
}:
mkPoetryApplication {
  projectDir = ./.;
  overrides = overrides.withDefaults(self: super: {});
}
#  overrides = overrides.withDefaults (self: super: {
#    mariadb = super.mariadb.overridePythonAttrs (old: {
#      nativeBuildInputs =
#        old.nativeBuildInputs ++ [libmysqlclient];
#    });
#    paho-mqtt = super.paho-mqtt.overridePythonAttrs(old: {
#        buildInputs = (old.buildInputs or [ ]) ++ [ super.hatchling ];
#    });
#    frozenlist = super.frozenlist.overridePythonAttrs(old: {
#        buildInputs = (old.buildInputs or [ ]) ++ [ super.tomli ];
#    });
#    yarl = super.yarl.overridePythonAttrs(old: {
#        buildInputs = (old.buildInputs or [ ]) ++ [ super.tomli ];
#    });
#    tomli = super.tomli.overridePythonAttrs(old: {
#        buildInputs = (old.buildInputs or [ ]) ++ [ super.flit-core ];
#    });
#  });
#}
