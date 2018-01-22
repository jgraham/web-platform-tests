function xvfb_start() {
    xvfb-run --server-args="-screen 0 $GEOMETRY -ac +extension RANDR" $@
}
