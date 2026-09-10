# ==========================================
# SMART PACKAGING AI CHATBOT
# ==========================================

KNOWLEDGE_BASE = {

    "indicator": {

        "title": "Active pH Bio-Indicators",

        "text": (
            "Active pH indicators utilize natural chromophores "
            "like Anthocyanins (red cabbage) or Curcumin (turmeric) "
            "immobilized onto bio-polymer films such as Chitosan, "
            "CMC and Sodium Alginate.\n\n"

            "Mechanism: As food spoils, volatile basic nitrogen "
            "compounds (TVB-N) or organic acids alter the film pH.\n\n"

            "Visual Shift: This triggers a color change such as "
            "Red -> Violet -> Green, which can be observed through "
            "a package window."
        )
    },


    "map": {

        "title": "Modified Atmosphere Packaging (MAP)",

        "text": (
            "MAP replaces the internal headspace air with specific "
            "gas formulations.\n\n"

            "High-Protein Dairy / Paneer: "
            "70% N2 / 30% CO2. CO2 can help inhibit aerobic mold growth.\n\n"

            "Fresh Produce / Greens: "
            "Equilibrium MAP may use approximately 3-5% O2 and "
            "5-10% CO2 to balance cellular respiration."
        )
    },


    "cold chain": {

        "title": "Cold Chain Integrity & Arrhenius Kinetics",

        "text": (
            "Cold-chain protection is important for temperature-sensitive "
            "food products.\n\n"

            "Temperature Abuse: Higher temperatures can accelerate "
            "chemical and biological degradation processes.\n\n"

            "Thermal Protection: Vacuum Insulation Panels (VIP) and "
            "Phase Change Materials (PCMs) can help reduce temperature "
            "fluctuations during long-distance transportation."
        )
    },


    "barrier": {

        "title": "High-Barrier Polymeric Films",

        "text": (
            "High-barrier packaging materials help protect food from "
            "oxygen, moisture and other environmental factors.\n\n"

            "OTR (Oxygen Transmission Rate): Low oxygen transmission "
            "helps reduce oxidation and rancidity.\n\n"

            "WVTR (Water Vapor Transmission Rate): Low water-vapor "
            "transmission helps control moisture transfer."
        )
    },


    "eco": {

        "title": "Biodegradable & Sustainable Materials",

        "text": (
            "Sustainable packaging can reduce dependence on conventional "
            "petroleum-based plastics.\n\n"

            "Bio-PLA (Polylactic Acid): A bio-based polymer commonly "
            "produced from fermented plant-derived sugars or starches.\n\n"

            "Nanocellulose Composites: Cellulose-based materials that "
            "can provide useful mechanical and barrier properties."
        )
    }
}


# ==========================================
# QUICK PROMPTS
# ==========================================

QUICK_PROMPTS = [

    "Tell me about pH indicators",

    "Explain MAP gas mixtures",

    "What is cold chain protection?",

    "What are biodegradable eco materials?",

    "What are high-barrier films?"
]


# ==========================================
# CHATBOT RESPONSE FUNCTION
# ==========================================

def get_chatbot_response(user_input):

    if not user_input:

        return {
            "title": "AI Advisor",
            "text": "Please enter a question."
        }


    user_lower = user_input.lower().strip()


    # --------------------------------------
    # EXIT CHECK
    # --------------------------------------

    if user_lower in [
        "exit",
        "quit",
        "back"
    ]:

        return {
            "title": "AI Advisor",
            "text": "Chat session ended."
        }


    # --------------------------------------
    # NUMBERED QUICK TOPICS
    # --------------------------------------

    if user_lower.isdigit():

        number = int(
            user_lower
        )

        topic_keys = list(
            KNOWLEDGE_BASE.keys()
        )

        if 1 <= number <= len(topic_keys):

            key = topic_keys[
                number - 1
            ]

            data = KNOWLEDGE_BASE[
                key
            ]

            return {
                "title": data["title"],
                "text": data["text"]
            }


    # --------------------------------------
    # KEYWORD MATCHING
    # --------------------------------------

    for key, data in KNOWLEDGE_BASE.items():

        keywords = [
            key
        ]


        # Additional keywords
        if key == "indicator":

            keywords.extend([
                "ph",
                "indicator",
                "indicators",
                "anthocyanin",
                "curcumin",
                "color change",
                "colour change"
            ])


        elif key == "map":

            keywords.extend([
                "modified atmosphere",
                "gas mixture",
                "gas mixtures",
                "nitrogen",
                "co2",
                "oxygen",
                "map packaging"
            ])


        elif key == "cold chain":

            keywords.extend([
                "cold",
                "temperature",
                "thermal",
                "arrhenius",
                "pcm",
                "pcms",
                "vip",
                "storage temperature"
            ])


        elif key == "barrier":

            keywords.extend([
                "barrier",
                "oxygen",
                "otr",
                "wvtr",
                "moisture",
                "polymer",
                "polymeric film"
            ])


        elif key == "eco":

            keywords.extend([
                "eco",
                "eco-friendly",
                "sustainable",
                "biodegradable",
                "bio pla",
                "pla",
                "nanocellulose",
                "green packaging"
            ])


        # Check keywords
        for keyword in keywords:

            if keyword in user_lower:

                return {
                    "title": data["title"],
                    "text": data["text"]
                }


    # --------------------------------------
    # DEFAULT RESPONSE
    # --------------------------------------

    return {

        "title": "Smart Packaging AI Advisor",

        "text": (
            "I can help with smart food packaging topics such as:\n\n"

            "• pH bio-indicators\n"
            "• Modified Atmosphere Packaging (MAP)\n"
            "• Cold-chain protection\n"
            "• High-barrier packaging films\n"
            "• Biodegradable and sustainable materials\n\n"

            "Try asking about one of these topics."
        )
    }


# ==========================================
# COMMAND-LINE VERSION
# ==========================================

def ask_chatbot():

    print("\n" + "=" * 65)

    print(
        "       SMART PACKAGING & COLD CHAIN AI ADVISOR"
    )

    print("=" * 65)

    print(
        "Status: Online | Domain Expert Knowledge Base"
    )

    print(
        "Type your question or type 'exit' to close.\n"
    )


    while True:

        print("\nSuggested Topics:")

        for index, prompt in enumerate(
            QUICK_PROMPTS,
            start=1
        ):

            print(
                f"{index}. {prompt}"
            )


        user_input = input(
            "\nUser: "
        ).strip()


        if user_input.lower() in [
            "exit",
            "quit",
            "back"
        ]:

            print(
                "\nAI Advisor: Closing chat session."
            )

            break


        result = get_chatbot_response(
            user_input
        )


        print(
            f"\nAI Advisor [{result['title']}]:"
        )

        print(
            result["text"]
        )


# ==========================================
# STANDALONE TEST
# ==========================================

if __name__ == "__main__":

    ask_chatbot()
