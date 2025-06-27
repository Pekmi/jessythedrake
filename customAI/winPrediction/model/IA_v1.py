import pandas as pd
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.metrics import roc_auc_score



df = pd.read_csv("draft_data.csv")

# Affiche la liste des colonnes
print("Colonnes du DataFrame :", df.columns.tolist())

# Sépare-les ensuite en deux listes pour les picks et les bans
pick_cols = [c for c in df.columns if c.startswith("blue_pick") or c.startswith("red_pick")]
ban_cols  = [c for c in df.columns if c.startswith("blue_ban")  or c.startswith("red_ban")]

print("Colonnes de picks :", pick_cols)
print("Colonnes de bans  :", ban_cols)
#on est censer avoir ca (verification) : Colonnes de picks : ['blue_pick_0', 'blue_pick_1', …, 'red_pick_4'] ; Colonnes de bans  : ['blue_ban_0', …, 'red_ban_4']


# 1. One-hot encoding pour chaque slot de pick et de ban
X_picks = pd.get_dummies(df[pick_cols].astype(str), prefix=pick_cols)
X_bans  = pd.get_dummies(df[ban_cols] .astype(str), prefix=ban_cols)

# 2. Concaténer les deux jeux de features
X = pd.concat([X_picks, X_bans], axis=1) #grande matrice, avec une colonne pour chaque pick et ban possible, et une ligne pour chaque match

'''Exemple de DataFrame X après concaténation :
| Match  | blue\_pick\_0\_10 | blue\_pick\_0\_20 | blue\_pick\_1\_10 | blue\_pick\_1\_30 | blue\_ban\_0\_15 | blue\_ban\_1\_20 |
| ------ | :---------------: | :---------------: | :---------------: | :---------------: | :--------------: | :--------------: |
| Match1 |         1         |         0         |         0         |         1         |         0        |         1        |
| Match2 |         0         |         1         |         1         |         0         |         1        |         0        |
ici, le champion numéro 10 a été choisi en tant que premier pick de l'équipe bleue, le champion numéro 20 a été choisi en tant que deuxième pick, etc.
Chaque colonne représente un champion spécifique, et la valeur 1 indique que ce champion a été choisi ou banni dans ce match, tandis que 0 indique qu'il ne l'a pas été.
'''

# 3. Afficher taille et quelques colonnes pour vérification
print("Shape de X :", X.shape)
print("Quelques colonnes de X :", X.columns.tolist()[:10])


# La cible binaire 0/1
y = df["result"]

# 1. On sépare d’abord Test (20 %) et Temporaire (80 %)
X_temp, X_test, y_temp, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# 2. On sépare ensuite Train (0.75*80=60 %) et Validation (0.25*80=20 %)
X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp,
    test_size=0.25,    # 0.25 × 80 % = 20 % du total
    random_state=42,
    stratify=y_temp
)

print("Train    :", X_train.shape, y_train.shape)   # ~60 % des données
print("Validation:", X_val.shape,   y_val.shape)     # ~20 %
print("Test     :", X_test.shape,  y_test.shape)    # 20 %



# 1. Prépare les DMatrix optimisés pour XGBoost
dtrain = xgb.DMatrix(X_train, label=y_train) # DMatrix est une structure de données optimisée pour XGBoost
dval   = xgb.DMatrix(X_val,   label=y_val)
dtest  = xgb.DMatrix(X_test,  label=y_test)

# 2. Définit les hyperparamètres de base
params = {
    "objective":        "binary:logistic",  # on prédit une probabilité
    "eval_metric":      "auc",              # on suit l'AUC sur valid
    "eta":              0.1,                # learning rate
    "max_depth":        6,                  # profondeur max des arbres
    "subsample":        0.8,                # fraction des lignes par arbre
    "colsample_bytree": 0.8,                # fraction des colonnes par arbre
    "seed":             42
}

# 3. Entraînement avec early stopping pour éviter le sur-apprentissage
bst = xgb.train(
    params,
    dtrain, # données d'entraînement
    num_boost_round=500, # nombre maximum d'arbres
    evals=[(dtrain, "train"), (dval, "valid")], 
    early_stopping_rounds=10, # arrête si pas d'amélioration en 10 rounds
    verbose_eval=10 # Affiche les métriques toutes les 10 itérations
)

# Une fois les hyperparamètres fixés, on évalue enfin sur Test
y_pred_test = bst.predict(dtest) # Prédictions sur le set de test
print("AUC finale sur Test :", roc_auc_score(y_test, y_pred_test))