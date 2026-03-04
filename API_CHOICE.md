# API Choice

- Étudiant : Damien Nadjar
- API choisie : Cat Facts API
- URL base : https://catfact.ninja
- Documentation officielle / README : https://catfact.ninja/
- Auth : None
- Endpoints testés :
  - GET /fact
- Hypothèses de contrat (champs attendus, types, codes) :
  - Code HTTP attendu : 200 OK
  - Format de réponse : JSON
  - Champs : `fact` (chaîne de caractères), `length` (entier)
- Limites / rate limiting connu : Aucune limite stricte documentée.
- Risques (instabilité, downtime, CORS, etc.) : Faible risque d'instabilité.
