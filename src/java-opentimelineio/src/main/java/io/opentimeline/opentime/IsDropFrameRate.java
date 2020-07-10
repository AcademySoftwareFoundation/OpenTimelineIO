package io.opentimeline.opentime;

public enum IsDropFrameRate {
    InferFromRate(-1),
    ForceNo(0),
    ForceYes(1);

    public final int index;

    private IsDropFrameRate(int index) {
        this.index = index;
    }

    public int getIndex() {
        return index;
    }
}
