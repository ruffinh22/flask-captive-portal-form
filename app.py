from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'votre_cle_secrete_ici' # N'oubliez pas de changer cette clé en production !

# Dossier pour sauvegarder les données
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@app.route('/')
def index():
    """Page d'accueil avec le formulaire"""
    return render_template('formulaire.html')

@app.route('/submit', methods=['POST'])
def submit_form():
    """Traiter la soumission du formulaire et sauvegarder dans un fichier JSON"""
    try:
        # Initialiser un dictionnaire pour stocker toutes les données du formulaire
        form_data = {}

        # --- Section 1: Informations Entreprise ---
        form_data['nom_entreprise'] = request.form.get('nom_entreprise')
        form_data['logo_format'] = request.form.get('logo_format')
        form_data['slogan'] = request.form.get('slogan')
        form_data['site_web'] = request.form.get('site_web')
        form_data['couleurs_marque'] = request.form.get('couleurs_marque')
        form_data['telephone_support'] = request.form.get('telephone_support')
        form_data['email_contact'] = request.form.get('email_contact')
        form_data['adresse'] = request.form.get('adresse')

        # --- Section 2: Configuration WiFi & Accès ---
        form_data['duree_session'] = request.form.get('duree_session')
        # Gérer le champ "Autre" pour la durée de session
        form_data['duree_session_autre'] = request.form.get('duree_session_autre') if form_data['duree_session'] == 'autre' else None

        form_data['modes_auth'] = request.form.getlist('modes_auth')
        # Gérer le champ "Autre" pour les modes d'authentification
        form_data['modes_auth_autre'] = request.form.get('modes_auth_autre_input') if 'autre_mode_auth' in form_data['modes_auth'] else None

        form_data['bande_passante'] = request.form.get('bande_passante')
        form_data['horaires_activation'] = request.form.get('horaires_activation')
        form_data['message_accueil'] = request.form.get('message_accueil')
        form_data['nb_max_utilisateurs'] = request.form.get('nb_max_utilisateurs')

        # --- Section 3: Intégration paiement Kkiapay ---
        form_data['cle_publique_kkiapay'] = request.form.get('cle_publique_kkiapay')
        form_data['devise'] = request.form.get('devise')
        # Gérer le champ "Autre" pour la devise
        form_data['devise_autre'] = request.form.get('devise_autre') if form_data['devise'] == 'autre' else None

        form_data['gestion_echecs'] = request.form.getlist('gestion_echecs')
        form_data['webhook_url'] = request.form.get('webhook_url')

        # Gérer les forfaits WiFi dynamiques (boucler sur les noms avec index)
        form_data['forfaits_wifi'] = []
        i = 1
        while True:
            nom = request.form.get(f'forfait_nom_{i}')
            prix = request.form.get(f'forfait_prix_{i}')
            # Si ni le nom ni le prix ne sont trouvés, on arrête
            if nom is None and prix is None:
                break
            # Si au moins un champ est rempli, on l'ajoute
            if nom or prix:
                form_data['forfaits_wifi'].append({'nom': nom, 'prix': prix})
            i += 1
        
        # --- Section 4: Contenu & Présence digitale ---
        # Gérer les pages additionnelles dynamiques
        form_data['pages_additionnelles'] = []
        i = 1
        while True:
            page_url = request.form.get(f'page_url_{i}')
            if page_url is None:
                break
            if page_url.strip(): # Ajouter seulement si le champ n'est pas vide
                form_data['pages_additionnelles'].append(page_url)
            i += 1

        form_data['contenu_multimedia'] = request.form.getlist('contenu_multimedia')
        
        # Gérer les liens sociaux (ils ont des noms fixes dans l'HTML mais on peut les collecter)
        form_data['liens_sociaux'] = {
            'facebook': request.form.get('facebook'),
            'instagram': request.form.get('instagram'),
            'linkedin': request.form.get('linkedin'),
            'tiktok': request.form.get('tiktok'),
            'youtube': request.form.get('youtube')
        }
        # Filtrer les liens sociaux qui sont vides
        form_data['liens_sociaux'] = {k: v for k, v in form_data['liens_sociaux'].items() if v}

        form_data['flux_afficher'] = request.form.getlist('flux_afficher')
        
        # --- Section 5: Services & Offres commerciales ---
        # Gérer les services/produits dynamiques
        form_data['services_produits'] = []
        i = 1
        while True:
            nom = request.form.get(f'service_nom_{i}')
            desc = request.form.get(f'service_desc_{i}')
            if nom is None and desc is None:
                break
            if nom or desc:
                form_data['services_produits'].append({'nom': nom, 'description': desc})
            i += 1

        form_data['formulaires_interaction'] = request.form.getlist('formulaires_interaction')
        form_data['photos_pro'] = request.form.get('photos_pro')
        form_data['description_activite'] = request.form.get('description_activite')
        form_data['promotion_speciale'] = request.form.get('promotion_speciale')
        
        # --- Section 6: Configuration technique & Analytics ---
        form_data['statistiques'] = request.form.getlist('statistiques')
        form_data['support_multilingue'] = request.form.get('support_multilingue')
        # Gérer le champ "Autre" pour les langues
        form_data['autres_langues'] = request.form.get('autres_langues') if form_data['support_multilingue'] == 'autre' else None

        form_data['gestion_donnees'] = request.form.getlist('gestion_donnees')
        form_data['niveau_support'] = request.form.get('niveau_support')

        # Gérer les intégrations avec autres systèmes dynamiques
        form_data['integrations_systemes'] = {}
        # Les champs fixes CRM et Email marketing
        crm_existant = request.form.get('crm_existant')
        if crm_existant:
            form_data['integrations_systemes']['crm_existant'] = crm_existant

        outil_email_marketing = request.form.get('outil_email_marketing')
        if outil_email_marketing:
            form_data['integrations_systemes']['outil_email_marketing'] = outil_email_marketing

        # Les champs "Autre outil" dynamiques
        i = 1
        while True:
            autre_outil = request.form.get(f'autre_outil_{i}')
            if autre_outil is None:
                break
            if autre_outil.strip(): # Ajouter seulement si le champ n'est pas vide
                form_data['integrations_systemes'][f'autre_outil_{i}'] = autre_outil
            i += 1
            
        # Métadonnées
        form_data['date_soumission'] = datetime.now().isoformat()
        form_data['ip_address'] = request.remote_addr # Attention: Peut être vide ou local en dev

        # Validation basique (peut être étendue)
        if not form_data.get('nom_entreprise') or not form_data.get('email_contact'):
            return render_template('error.html', error="Le nom de l'entreprise et l'email de contact sont obligatoires."), 400
        
        # Sauvegarder dans un fichier JSON
        # Utilisez le nom de l'entreprise pour rendre le nom de fichier plus identifiable
        # Nettoyez le nom de l'entreprise pour le rendre compatible avec les noms de fichiers
        clean_company_name = ''.join(c for c in form_data['nom_entreprise'] if c.isalnum() or c in [' ', '-']).replace(' ', '_')
        filename = f"questionnaire_{clean_company_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(DATA_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(form_data, f, ensure_ascii=False, indent=2)
        
        return render_template('success.html', filename=filename)
    
    except Exception as e:
        # Log l'erreur complète pour le débogage en mode debug
        app.logger.error(f"Erreur lors de la soumission du formulaire : {e}", exc_info=True)
        return render_template('error.html', error=f"Une erreur interne est survenue : {str(e)}"), 500

@app.route('/admin')
def admin():
    """Page d'administration pour voir les soumissions"""
    files = []
    if os.path.exists(DATA_DIR):
        # Trie les fichiers par date de modification pour voir les plus récents en premier
        sorted_files = sorted(os.listdir(DATA_DIR), key=lambda f: os.path.getmtime(os.path.join(DATA_DIR, f)), reverse=True)
        for filename in sorted_files:
            if filename.endswith('.json'):
                filepath = os.path.join(DATA_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    files.append({
                        'filename': filename,
                        'nom_entreprise': data.get('nom_entreprise', 'Non spécifié'),
                        'date_soumission': data.get('date_soumission', 'Non spécifié'),
                        'email_contact': data.get('email_contact', 'Non spécifié')
                    })
                except json.JSONDecodeError:
                    # Gérer les fichiers JSON corrompus ou mal formés
                    app.logger.warning(f"Fichier JSON corrompu ou mal formé: {filename}. Il sera ignoré.")
                    files.append({
                        'filename': filename,
                        'nom_entreprise': 'Erreur de lecture',
                        'date_soumission': 'N/A',
                        'email_contact': 'N/A'
                    })
                except Exception as e:
                    app.logger.error(f"Erreur inattendue lors de la lecture du fichier {filename}: {e}")
                    files.append({
                        'filename': filename,
                        'nom_entreprise': 'Erreur inattendue',
                        'date_soumission': 'N/A',
                        'email_contact': 'N/A'
                    })
    
    return render_template('admin.html', files=files)

@app.route('/view/<filename>')
def view_submission(filename):
    """Voir une soumission spécifique"""
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return render_template('view.html', data=data, filename=filename)
        except json.JSONDecodeError:
            return "Le fichier de soumission est corrompu ou mal formé.", 500
        except Exception as e:
            app.logger.error(f"Erreur lors de l'affichage du fichier {filename}: {e}")
            return f"Une erreur s'est produite lors de l'affichage du fichier : {str(e)}", 500
    else:
        return "Fichier non trouvé", 404

# --- Nouvelle route pour supprimer une soumission (utile pour l'administration) ---
@app.route('/delete/<filename>', methods=['POST'])
def delete_submission(filename):
    """Supprimer une soumission spécifique"""
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            # Rediriger vers la page admin avec un message de succès
            return redirect(url_for('admin', message='Soumission supprimée avec succès!'))
        except Exception as e:
            app.logger.error(f"Erreur lors de la suppression du fichier {filename}: {e}")
            return redirect(url_for('admin', error=f"Erreur lors de la suppression: {str(e)}"))
    else:
        return "Fichier non trouvé", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)