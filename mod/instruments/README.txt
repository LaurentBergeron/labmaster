Every instrument related thing.

The function available_instruments() should be modified when adding a new instrument to the program.
Define the Lab class, a Drawer class designed to keep Instrument instances. Lab also takes care of timing and managing instructions for memory loading.
Define the Instrument class.
Define all the classes specific to instruments.

Rules
- Each instrument needs a close(self) method.
- Each instrument needs a abort(self) method.
- Each instrument with the attribute has_memory=True needs a load_memory(self) method.
- Each instrument with the attribute has_memory=True and is_ping_pong=True needs a load_memory_ping_pong(self) method.