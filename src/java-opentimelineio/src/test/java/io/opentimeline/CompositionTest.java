package io.opentimeline;

import io.opentimeline.opentimelineio.Composable;
import io.opentimeline.opentimelineio.Composition;
import io.opentimeline.opentimelineio.ErrorStatus;
import io.opentimeline.opentimelineio.Item;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class CompositionTest {

    @Test
    public void testConstructor() {
        Item item = new Item.ItemBuilder().build();
        Composition composition = new Composition.CompositionBuilder()
                .setName("test")
                .build();
        ErrorStatus errorStatus = new ErrorStatus();
        assertTrue(composition.appendChild(item, errorStatus));
        assertEquals(composition.getName(), "test");
        assertTrue(composition.getChildren().get(0).isEquivalentTo(item));
        assertEquals(composition.getCompositionKind(), "Composition");
    }

}
