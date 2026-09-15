import os
import sys
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.database import SessionLocal, engine, Base
from backend import models
from backend.auth import get_password_hash
from backend.routers.products_router import calculate_viability_score
from backend.routers.suppliers_router import compute_reliability
from backend.routers.compliance_router import generate_default_category_rules

def seed_database():
    print("🌱 Initialisation de la base de données MVB...")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        admin_email = "admin@mvb-platform.com"
        user = db.query(models.User).filter(models.User.email == admin_email).first()
        if not user:
            print("👤 Création de l'utilisateur Démo Admin...")
            user = models.User(
                email=admin_email,
                hashed_password=get_password_hash("admin123456"),
                full_name="Alexandre Fondateur MVB",
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        seed_products = [
            {
                "title": "Correcteur de Posture Ergonomique Pro",
                "category": "Santé & Bien-être",
                "description": "Dispositif médical léger ajustant la posture dorsale et cervicale avec capteur de vibration intelligent.",
                "selling_price": 44.99,
                "estimated_cogs": 8.50,
                "estimated_shipping": 3.80,
                "estimated_cac": 12.00,
                "search_volume": 18500,
                "competition_level": "Medium",
                "complexity_score": 1,
                "fragility_score": 1,
                "customer_rating": 4.8,
                "supplier": {
                    "name": "Shenzhen PostureCare Health Ltd",
                    "platform": "Alibaba",
                    "years_in_business": 6,
                    "is_verified": True,
                    "response_rate": 97.5,
                    "unit_price": 7.50,
                    "min_order_quantity": 100,
                    "shipping_cost": 2.20,
                    "lead_time_days": 10,
                    "customization_cost": 0.80
                },
                "landing_slug": "correcteur-posture-pro",
                "marketing": {
                    "script_hook": "Arrêtez de vous voûter devant votre écran ! 🛑 Ce petit capteur va rééduquer votre dos.",
                    "script_problem": "Mal de dos à la fin de la journée ? Les mauvaises postures au bureau détruisent vos vertèbres.",
                    "script_solution": "Le Correcteur Pro vibre doucement dès que vous vous avachissez pour vous redresser instantanément.",
                    "script_cta": "Commandez votre Correcteur Pro aujourd'hui et profitez de -40% + Livraison Express !"
                }
            },
            {
                "title": "Gourde Isotherme Éco-Design 750ml",
                "category": "Cuisine & Sport",
                "description": "Bouteille réutilisable double paroi inox 314 gardant le chaud 12h et le froid 24h avec bouchon bambou.",
                "selling_price": 29.99,
                "estimated_cogs": 5.20,
                "estimated_shipping": 2.90,
                "estimated_cac": 8.50,
                "search_volume": 24000,
                "competition_level": "Low",
                "complexity_score": 1,
                "fragility_score": 2,
                "customer_rating": 4.7,
                "supplier": {
                    "name": "Ningbo EcoDrinkware Mfg Co.",
                    "platform": "Grossiste",
                    "years_in_business": 4,
                    "is_verified": True,
                    "response_rate": 93.0,
                    "unit_price": 4.80,
                    "min_order_quantity": 200,
                    "shipping_cost": 1.90,
                    "lead_time_days": 12,
                    "customization_cost": 0.40
                },
                "landing_slug": "gourde-isotherme-eco",
                "marketing": {
                    "script_hook": "Dites adieu aux bouteilles en plastique jetables ! 🌿",
                    "script_problem": "Votre eau devient tiède au bout de 20 minutes pendant le sport ou au bureau ?",
                    "script_solution": "Cette gourde en acier inox conserve votre boisson glacée pendant 24h sans altérer le goût.",
                    "script_cta": "Rejoignez le mouvement zéro déchet : profitez du pack 2 gourdes à prix réduit !"
                }
            },
            {
                "title": "Mangeoire Intelligente Caméra HD Chat & Chien",
                "category": "Électronique & Animalerie",
                "description": "Distributeur automatique de croquettes connecté Wi-Fi avec caméra grand angle 1080p et microphone bidirectionnel.",
                "selling_price": 99.99,
                "estimated_cogs": 24.00,
                "estimated_shipping": 6.00,
                "estimated_cac": 22.00,
                "search_volume": 11200,
                "competition_level": "Low",
                "complexity_score": 3,
                "fragility_score": 3,
                "customer_rating": 4.9,
                "supplier": {
                    "name": "Guangzhou SmartPet Electronics",
                    "platform": "Agent",
                    "years_in_business": 2,
                    "is_verified": False,
                    "response_rate": 84.0,
                    "unit_price": 22.50,
                    "min_order_quantity": 30,
                    "shipping_cost": 5.50,
                    "lead_time_days": 18,
                    "customization_cost": 2.00
                },
                "landing_slug": "mangeoire-intelligente-hd",
                "marketing": {
                    "script_hook": "Voyez ce que fait votre chat quand vous n'êtes pas là ! 🐱🎥",
                    "script_problem": "Inquiet pour les repas de votre animal de compagnie pendant vos longues journées de travail ?",
                    "script_solution": "Nourrissez-le à distance depuis votre smartphone et parlez-lui en direct via la caméra HD intégrée.",
                    "script_cta": "Offrez le meilleur confort à votre compagnon : -30€ ce week-end seulement !"
                }
            }
        ]

        for p_data in seed_products:
            existing_prod = db.query(models.Product).filter(
                models.Product.title == p_data["title"],
                models.Product.user_id == user.id
            ).first()

            if not existing_prod:
                print(f"📦 Ajout du produit : {p_data['title']}")
                from backend.schemas import ProductBase
                base_p = ProductBase(
                    title=p_data["title"],
                    category=p_data["category"],
                    description=p_data["description"],
                    selling_price=p_data["selling_price"],
                    estimated_cogs=p_data["estimated_cogs"],
                    estimated_shipping=p_data["estimated_shipping"],
                    estimated_cac=p_data["estimated_cac"],
                    search_volume=p_data["search_volume"],
                    competition_level=p_data["competition_level"],
                    complexity_score=p_data["complexity_score"],
                    fragility_score=p_data["fragility_score"],
                    customer_rating=p_data["customer_rating"]
                )
                viability = calculate_viability_score(base_p)

                product = models.Product(
                    title=p_data["title"],
                    category=p_data["category"],
                    description=p_data["description"],
                    selling_price=p_data["selling_price"],
                    estimated_cogs=p_data["estimated_cogs"],
                    estimated_shipping=p_data["estimated_shipping"],
                    estimated_cac=p_data["estimated_cac"],
                    search_volume=p_data["search_volume"],
                    competition_level=p_data["competition_level"],
                    complexity_score=p_data["complexity_score"],
                    fragility_score=p_data["fragility_score"],
                    customer_rating=p_data["customer_rating"],
                    viability_score=viability,
                    user_id=user.id
                )
                db.add(product)
                db.commit()
                db.refresh(product)

                s_data = p_data["supplier"]
                is_rel = compute_reliability(s_data["years_in_business"], s_data["is_verified"], s_data["response_rate"])
                supplier = models.Supplier(
                    name=s_data["name"],
                    platform=s_data["platform"],
                    years_in_business=s_data["years_in_business"],
                    is_verified=s_data["is_verified"],
                    response_rate=s_data["response_rate"],
                    unit_price=s_data["unit_price"],
                    min_order_quantity=s_data["min_order_quantity"],
                    shipping_cost=s_data["shipping_cost"],
                    lead_time_days=s_data["lead_time_days"],
                    customization_cost=s_data["customization_cost"],
                    is_reliable=is_rel,
                    product_id=product.id
                )
                db.add(supplier)

                landing = models.LandingPage(
                    slug=p_data["landing_slug"],
                    title=f"Landing - {product.title}",
                    main_headline=f"Découvrez {product.title}",
                    subheadline=product.description,
                    selling_points=[
                        "✔️ Conception ergonomique brevetée et approuvée par les experts",
                        "✔️ Matériaux durables de qualité supérieure",
                        "✔️ Livraison express 24/48h & Suivi en temps réel",
                        "✔️ Satisfait ou 100% Remboursé sous 30 jours"
                    ],
                    faq_list=[
                        {"question": "Quels sont les délais de livraison ?", "answer": "Expédition sous 24h, livraison à domicile en 2 à 4 jours ouvrés."},
                        {"question": "Quelle est la politique de retour ?", "answer": "Retour simple et gratuit sans justification sous 30 jours."}
                    ],
                    call_to_action="Commander avec -30% Réduction",
                    click_count=24,
                    email_count=8,
                    product_id=product.id,
                    user_id=user.id
                )
                db.add(landing)

                rules = generate_default_category_rules(product.category)
                compliance = models.ComplianceCheck(
                    product_id=product.id,
                    category=product.category,
                    ce_marking=rules["ce_marking"],
                    rohs_compliant=rules["rohs_compliant"],
                    mandatory_labeling=rules["mandatory_labeling"],
                    custom_rules=rules["custom_rules"],
                    eori_number="FR123456789000",
                    notes="Statut documentaire valide pour l'importation UE."
                )
                db.add(compliance)

                doc = models.ImportDocument(
                    product_id=product.id,
                    doc_type="Certificat CE",
                    doc_name=f"Certificat_Conformite_{product.id}.pdf",
                    status="Validated"
                )
                db.add(doc)

                m_data = p_data["marketing"]
                mkt = models.MarketingContent(
                    product_id=product.id,
                    script_hook=m_data["script_hook"],
                    script_problem=m_data["script_problem"],
                    script_solution=m_data["script_solution"],
                    script_cta=m_data["script_cta"],
                    ad_copy_meta=f"🌟 {product.title}\n\n{product.description}\n\n👉 Profitez de notre réduction limitée à -30% !",
                    ad_copy_tiktok=f"Ce {product.title} fait un carton sur TikTok 🔥 Lien en bio pour commander !"
                )
                db.add(mkt)

                sav = models.CustomerSupportTemplate(
                    product_id=product.id,
                    inquiry_type="Shipping",
                    customer_email="client.demo@example.com",
                    incoming_message="Bonjour, je voudrais savoir quand ma commande arrivera ?",
                    generated_reply=f"Bonjour,\n\nMerci pour votre achat du {product.title} ! Votre colis a été expédié et est en cours d'acheminement avec numéro de suivi. Il arrivera sous 48h.\n\nExcellente journée à vous !"
                )
                db.add(sav)

                db.commit()

        print("✅ Base de données pré-alimentée avec succès !")
        print(f"📧 Identifiant Admin : {admin_email}")
        print("🔑 Mot de passe Admin : admin123456")

    except Exception as e:
        db.rollback()
        print(f"❌ Erreur lors du seeding : {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
