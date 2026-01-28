import { useState } from "react";

const App: React.FC = () => {
  const [prompt, setPrompt] = useState<string>("");
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const apiKey = import.meta.env.RUNPOD_API_KEY as string;
  const endpointId = import.meta.env.RUNPOD_ENDPOINT_ID as string;

  const generateImage = async (): Promise<void> => {
    if (!prompt) {
      alert("Please enter a prompt!");
      return;
    }

    setLoading(true);
    setImageUrl(null);

    const options: RequestInit = {
      method: "POST",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
        authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        input: {
          prompt,
          num_inference_steps: 25,
          width: 1024,
          height: 1024,
          guidance_scale: 7.5,
          seed: null,
          num_images: 1,
        },
      }),
    };

    try {
      const response = await fetch(
        `https://api.runpod.ai/v2/${endpointId}/runsync`,
        options
      );
      const data: { output?: string } = await response.json();
      if (data && data.output) {
        setImageUrl(`data:image/jpeg;base64,${data.output}`);
      } else {
        alert("Failed to generate image");
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Error generating image");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ textAlign: "center", padding: "20px", fontFamily: "Arial" }}>
      <h1>RunPod AI Image Generator</h1>
      <input
        type="text"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Enter your image prompt"
        style={{ padding: "10px", width: "300px" }}
      />
      <button onClick={generateImage} style={{ marginLeft: "10px", padding: "10px" }}>
        Generate Image
      </button>

      {loading && <p>Generating...</p>}

      <div id="imageResult" style={{ marginTop: "20px" }}>
        {imageUrl && <img src={imageUrl} alt="Generated" style={{ maxWidth: "100%" }} />}
      </div>
    </div>
  );
};

export default App;