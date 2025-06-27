import pkg_resources

required = {'numpy', 'pandas', 'scikit-learn', 'xgboost'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    print("🛑 Il manque ces paquets :", missing)
else:
    print("✅ Toutes les bibliothèques sont installées.")
