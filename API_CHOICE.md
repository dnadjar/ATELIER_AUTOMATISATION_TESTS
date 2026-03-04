# API Choice

- Étudiant : Damiennadjar
- API choisie : ExchangeRate-API
- URL base : https://api.exchangerate-api.com
- Documentation officielle / README : https://www.exchangerate-api.com/docs/free
- Auth : None
- Endpoints testés :
  - GET /v4/latest/USD
- Hypothèses de contrat (champs attendus, types, codes) :
  - Code HTTP attendu : 200 OK
  - Format de réponse : JSON
  - Champs : `fact` (chaîne de caractères), `length` (entier)
- Limites / rate limiting connu : Aucune limite stricte documentée.
- Risques (instabilité, downtime, CORS, etc.) : Faible risque d'instabilité.
