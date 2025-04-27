def analyse_image_openai(file_url):
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Analyse cette image d'immeuble et déduis uniquement :\n\n"
                                "- Le **type** : Maison individuelle ou Immeuble collectif\n"
                                "- Le **nombre d'étages** : RDC = 0, R+1 = 1, etc.\n"
                                "- La **catégorie fiscale** selon le décret sénégalais (1, 2, 3 pour individuel ou A, B, C pour collectif)\n"
                                "- Fais une déduction précise sans inventer.\n"
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": file_url
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.2,
            "max_tokens": 500
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        if response.status_code == 200:
            output = response.json()
            content = output["choices"][0]["message"]["content"]
            return content
        else:
            return f"❌ Erreur OpenAI Vision : {response.status_code} - {response.json()}"

    except Exception as e:
        return f"❌ Exception : {e}"
