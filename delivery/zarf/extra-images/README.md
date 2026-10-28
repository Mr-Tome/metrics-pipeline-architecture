# Extra images

The image scan in `20-build-zarf-package.sh` reads rendered Helm output. If a chart pulls an
image the scan cannot see (for example a bare `busybox` with no registry), staging will show it as
`ImagePullBackOff`. Add the full reference here in a file named after the component:

    GPU_OPERATOR.txt   DATABASE.txt   GATEWAY.txt   CHAT.txt

One image per line, for example `docker.io/library/busybox:1.37.0`. Lines starting with `#` are ignored.
