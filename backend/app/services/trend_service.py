class TrendService:

    @staticmethod
    def get_topics(niche: str):

        topics = {

            "Morning Spiritual": [

                "Morning Gratitude",

                "Power of Prayer",

                "Start Your Day with Positivity",

                "Inner Peace"

            ],

            "Financial Freedom": [

                "Why Rich Stay Rich",

                "Money Habits",

                "Passive Income",

                "Financial Discipline"

            ],

            "Cosmic Knowledge": [

                "Dark Matter",

                "Parallel Universe",

                "Black Hole Mystery",

                "Time Travel"

            ],

            "Psychology": [

                "Halo Effect",

                "Silent People",

                "Human Behavior",

                "Overthinking"

            ],

            "Love & Romantic": [

                "True Love",

                "Soulmate",

                "Long Distance Love",

                "Love Psychology"

            ]

        }

        return topics.get(niche, [])