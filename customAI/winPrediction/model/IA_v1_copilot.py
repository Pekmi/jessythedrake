import pandas as pd
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix
import numpy as np



df = pd.read_csv("draft_data.csv")

# === ANALYSE EXPLORATOIRE DES DONNÉES ===
print("=== INFORMATIONS GÉNÉRALES ===")
print(f"Taille du dataset : {df.shape[0]} matchs, {df.shape[1]} colonnes")
print(f"Valeurs manquantes : {df.isnull().sum().sum()}")

# Analyse de la variable cible
print("\n=== ANALYSE DE LA VARIABLE CIBLE ===")
print("Distribution des résultats :")
print(df["result"].value_counts())
print(f"Proportion de victoires équipe bleue : {df['result'].mean():.3f}")

# Vérification du side bias (avantage équipe bleue vs rouge)
if df["result"].mean() != 0.5:
    print(f"⚠️  Side bias détecté ! L'équipe bleue a un avantage de {abs(df['result'].mean() - 0.5)*100:.1f}%")
else:
    print("✅ Pas de side bias détecté")

print("\n=== COLONNES DU DATASET ===")
# Affiche la liste des colonnes
print("Colonnes du DataFrame :", df.columns.tolist())

# Sépare-les ensuite en deux listes pour les picks et les bans
pick_cols = [c for c in df.columns if c.startswith("blue_pick") or c.startswith("red_pick")]
ban_cols  = [c for c in df.columns if c.startswith("blue_ban")  or c.startswith("red_ban")]

print("\n=== ANALYSE DES COLONNES DRAFT ===")
print("Colonnes de picks :", pick_cols)
print("Colonnes de bans  :", ban_cols)
print(f"Nombre de picks par équipe : {len([c for c in pick_cols if c.startswith('blue_pick')])}")
print(f"Nombre de bans par équipe : {len([c for c in ban_cols if c.startswith('blue_ban')])}")

# Analyse des champions les plus populaires
print("\n=== CHAMPIONS LES PLUS POPULAIRES ===")
all_picks = pd.concat([df[col] for col in pick_cols]).dropna()
top_picks = all_picks.value_counts().head(10)
print("Top 10 champions les plus pickés :")
for champ, count in top_picks.items():
    print(f"  Champion {champ}: {count} fois ({count/len(df)*100:.1f}%)")

all_bans = pd.concat([df[col] for col in ban_cols]).dropna()
top_bans = all_bans.value_counts().head(10)
print("\nTop 10 champions les plus bannis :")
for champ, count in top_bans.items():
    print(f"  Champion {champ}: {count} fois ({count/len(df)*100:.1f}%)")

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
print("\n=== FEATURES APRÈS PREPROCESSING ===")
print("Shape de X :", X.shape)
print("Quelques colonnes de X :", X.columns.tolist()[:10])
print(f"Nombre total de features : {X.shape[1]}")
print(f"Sparsité de la matrice : {(X == 0).sum().sum() / (X.shape[0] * X.shape[1]):.3f}")

# Vérification de la cohérence des données
print("\n=== VÉRIFICATIONS DE COHÉRENCE ===")
# Chaque match doit avoir exactement 5 picks par équipe
picks_per_match = X[[col for col in X.columns if 'pick' in col]].sum(axis=1)
print(f"Picks par match - Min: {picks_per_match.min()}, Max: {picks_per_match.max()}, Moyenne: {picks_per_match.mean():.1f}")

# Chaque match doit avoir exactement le bon nombre de bans
bans_per_match = X[[col for col in X.columns if 'ban' in col]].sum(axis=1)
print(f"Bans par match - Min: {bans_per_match.min()}, Max: {bans_per_match.max()}, Moyenne: {bans_per_match.mean():.1f}")


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

# Vérification de la stratification
print(f"\nDistribution dans Train : {y_train.mean():.3f}")
print(f"Distribution dans Validation : {y_val.mean():.3f}")
print(f"Distribution dans Test : {y_test.mean():.3f}")



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

# === ÉVALUATION COMPLÈTE DU MODÈLE ===
print("\n" + "="*50)
print("         RÉSULTATS FINAUX")
print("="*50)

# AUC Score
auc_score = roc_auc_score(y_test, y_pred_test)
print(f"AUC finale sur Test : {auc_score:.4f}")

# Classification binaire (seuil 0.5)
y_pred_binary = (y_pred_test > 0.5).astype(int)
accuracy = (y_pred_binary == y_test).mean()
print(f"Accuracy sur Test : {accuracy:.4f}")

# Rapport de classification détaillé
print("\n=== RAPPORT DE CLASSIFICATION ===")
print(classification_report(y_test, y_pred_binary, 
                          target_names=['Red Team Win', 'Blue Team Win']))

# Matrice de confusion
print("\n=== MATRICE DE CONFUSION ===")
cm = confusion_matrix(y_test, y_pred_binary)
print("                 Prédiction")
print("Réalité    Red Win    Blue Win")
print(f"Red Win      {cm[0,0]:6d}      {cm[0,1]:6d}")
print(f"Blue Win     {cm[1,0]:6d}      {cm[1,1]:6d}")

# Analyse des prédictions
print(f"\n=== ANALYSE DES PRÉDICTIONS ===")
print(f"Probabilité moyenne prédite : {y_pred_test.mean():.3f}")
print(f"Probabilité min : {y_pred_test.min():.3f}")
print(f"Probabilité max : {y_pred_test.max():.3f}")

# Features les plus importantes
print(f"\n=== TOP 20 FEATURES LES PLUS IMPORTANTES ===")
try:
    feature_importance = bst.get_score(importance_type='weight')
    top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:20]
    for i, (feat, score) in enumerate(top_features, 1):
        print(f"{i:2d}. {feat}: {score}")
except:
    print("Impossible d'afficher l'importance des features")

print("\n" + "="*50)




#améliorations ajoutées
'''Améliorations ajoutées :
1. Analyse Exploratoire des Données
✅ Vérification de la taille du dataset et valeurs manquantes
✅ Analyse du side bias (avantage équipe bleue vs rouge)
✅ Champions les plus populaires (picks et bans)
✅ Vérification de la cohérence des données (nombre de picks/bans par match)
2. Métriques d'Évaluation Complètes
✅ AUC (déjà présent)
✅ Accuracy
✅ Classification Report (précision, rappel, f1-score)
✅ Matrice de Confusion
✅ Analyse des probabilités prédites
3. Analyse des Features Importantes
✅ Top 20 features les plus importantes selon XGBoost
✅ Informations sur la sparsité de votre matrice
4. Vérifications de Qualité
✅ Vérification de la stratification des données
✅ Contrôle de cohérence (5 picks par équipe, etc.)'''


#pour plus tard :
'''Prochaines étapes suggérées :
Lancez le code pour voir les résultats de cette analyse
Analysez le side bias - si > 5% d'écart, il faudra en tenir compte
Regardez les champions dominants - certains sont-ils trop puissants ?
Examinez les features importantes - sont-ce des champions attendus ?'''