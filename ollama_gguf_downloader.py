import requests
import json
import os

def display_intro():
    print(r"""
  _____       _                           _   _  __ _
 / ____|     | |                         | | | |/ _| |
| |  __  ___ | |_   _ __ ___   __ _ _ __ | |_| | |_| | _____  __
| | |_ |/ _ \| | | | | '_ ` _ \ / _` | '_ \| __| |  _| |/ _ \ \/ /
| |__| | (_) | | |_| | | | | | | (_| | | | | |_| | | | |  __/>  <
 \_____|\___/|_|\__, |_| |_| |_|\__,_|_| |_|\__|_|_| |_|\___/_/\_\
                 __/ |
                |___/
    """)
    print("Welcome to the Ollama GGUF Model Downloader!")
    print("This script helps you download models directly from the Ollama library in GGUF format.\n")
    print("You'll need to provide:")
    print("- Model name (e.g., 'phi3')")
    print("- Model parameters (e.g., '3.8b')")
    print("\nLet's get started!\n")

def get_model_info():
    model_name = input("Enter the model name (e.g., 'phi3'): ").strip()
    model_params = input("Enter the model parameters (e.g., '3.8b'): ").strip()
    return model_name, model_params

def get_model_details(model_name, model_params):
    """Get both the manifest and metadata for the model"""
    manifest_url = f"https://registry.ollama.ai/v2/library/{model_name}/manifests/{model_params}"
    headers = {
        'User-Agent': 'GGUF-Downloader/1.0',
        'Accept': 'application/vnd.docker.distribution.manifest.v2+json, application/vnd.oci.image.manifest.v1+json'
    }

    try:
        response = requests.get(manifest_url, headers=headers)
        response.raise_for_status()
        manifest = response.json()

        # Initialize default values
        model_digest = None
        config_data = {
            'model_family': model_name,
            'model_type': model_params,
            'file_type': 'Q4_0'  # Default quantization
        }

        # First, try to find a layer specifically marked as a model
        for layer in manifest.get('layers', []):
            if layer.get('mediaType') == 'application/vnd.ollama.image.model':
                model_digest = layer['digest'].split(':')[-1]
                break

        # If we didn't find a model layer, try the config approach
        if not model_digest and 'config' in manifest and 'digest' in manifest['config']:
            config_digest = manifest['config']['digest'].split(':')[-1]

            # Get config blob to find the actual model file
            config_url = f"https://registry.ollama.ai/v2/library/{model_name}/blobs/sha256:{config_digest}"
            config_response = requests.get(config_url, headers=headers)
            config_response.raise_for_status()

            try:
                temp_config_data = config_response.json()

                # Update our config data with any values from the response
                if isinstance(temp_config_data, dict):
                    config_data.update({
                        'model_family': temp_config_data.get('model_family', config_data['model_family']),
                        'model_type': temp_config_data.get('model_type', config_data['model_type']),
                        'file_type': temp_config_data.get('file_type', config_data['file_type'])
                    })

                # Look for the rootfs diff_ids, which should point to the model layer
                if 'rootfs' in temp_config_data and 'diff_ids' in temp_config_data['rootfs'] and temp_config_data['rootfs']['diff_ids']:
                    # Usually the first layer contains the model
                    model_digest = temp_config_data['rootfs']['diff_ids'][0].split(':')[-1]
            except json.JSONDecodeError:
                print("Warning: Could not parse config as JSON, using default digest extraction.")

        # If we still don't have a digest, try to use the first layer as a fallback
        if not model_digest and 'layers' in manifest and manifest['layers']:
            model_digest = manifest['layers'][0]['digest'].split(':')[-1]
            print("Warning: Using first layer as fallback. This may not be the correct model data.")

        if not model_digest:
            raise ValueError("Could not find model data in the manifest")

        return {
            'digest': model_digest,
            'model_family': config_data['model_family'],
            'model_type': config_data['model_type'],
            'file_type': config_data['file_type']
        }

    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch model details: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse response as JSON. The server may have returned an unexpected response.")

def download_model(model_name, model_details, filename):
    digest = model_details['digest']
    url = f"https://registry.ollama.ai/v2/library/{model_name}/blobs/sha256:{digest}"
    headers = {
        'User-Agent': 'GGUF-Downloader/1.0',
        'Accept': 'application/octet-stream'  # Explicitly request binary data
    }

    try:
        with requests.get(url, headers=headers, stream=True) as response:
            response.raise_for_status()

            # Check if we actually got binary data and not JSON
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                # Try to parse the JSON to see if it's an error message
                try:
                    error_data = response.json()
                    raise Exception(f"Server returned JSON instead of binary data: {json.dumps(error_data)}")
                except json.JSONDecodeError:
                    raise Exception("Server returned JSON instead of binary data but couldn't parse it")

            # Get the total size for progress tracking
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Show progress
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            mb_downloaded = downloaded / (1024 * 1024)
                            mb_total = total_size / (1024 * 1024)
                            print(f"Downloaded: {mb_downloaded:.2f} MB / {mb_total:.2f} MB ({percent:.1f}%)", end='\r')
                        else:
                            print(f"Downloaded: {downloaded/1024/1024:.2f} MB", end='\r')

            print(f"\nDownload complete! Saved as {filename}")
            return True

    except requests.exceptions.RequestException as e:
        if os.path.exists(filename):
            os.remove(filename)  # Remove partial download
        raise Exception(f"Download failed: {str(e)}")

def main():
    display_intro()

    try:
        model_name, model_params = get_model_info()

        print("\n🛠  Fetching model information...")
        model_details = get_model_details(model_name, model_params)
        digest = model_details['digest']
        print(f"✅ Successfully retrieved model digest: {digest[:12]}...")

        # Construct a more descriptive default filename
        default_filename = f"{model_name}-{model_params}-{model_details['file_type']}.gguf"
        filename = input(f"\n📝 Enter output filename (default: {default_filename}): ").strip() or default_filename

        print("\n⬇️  Starting download...")
        download_model(model_name, model_details, filename)

        print("\n🎉 All done! Happy AI experimenting!")
        print(f"You can now use this model with llama.cpp based tools like koboldcpp.")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nPossible reasons:")
        print("- Incorrect model name or parameters")
        print("- Network connection issues")
        print("- Changes in Ollama's API structure")
        print("- The model might not be available in GGUF format")
        print("\nPlease check your inputs and try again.")

if __name__ == "__main__":
    main()
