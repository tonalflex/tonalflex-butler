# Butler CI/CD

This repository uses GitHub Actions to build and release the Butler binary.

## 🚀 Releasing a new version

To tag and push a new release (e.g. `v0.0.1`):

```sh
git tag v0.0.1
git push origin v0.0.1
```

This triggers the GitHub Actions workflow to:

- Generate Protobuf files
- Build the binary for Linux ARM64
- Package it as a `.tar.gz`
- Upload to GitHub Releases

## 🧪 Running CI locally with `act`

You can run GitHub Actions locally using [`act`](https://github.com/nektos/act).

### 1. Install `act`

```sh
brew install act
```

### 2. Run the workflow

```sh
ACT=true act workflow_dispatch --container-architecture linux/amd64
```

> On Apple Silicon (M1/M2/M3), `--container-architecture linux/amd64` is required to avoid compatibility issues.

## ⚠️ Limitations of `act`

`act` does **not** support `upload-artifact` or `download-artifact`.

These steps are skipped automatically when `ACT=true`. Ensure:

- The `proto` files exist before running the build
- The `dist` output is saved to a shared path (e.g., `./build/dist`)

## 🐳 Docker alternative

You can also run the build process manually using Docker Compose:

```sh
docker compose run --rm proto-generator
docker compose run --rm butler-arm64-builder
```
