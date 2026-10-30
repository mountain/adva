#[path = "native_input_binding_certificate.rs"]
mod producer;

#[test]
fn separately_compiled_consumer_receives_only_matching_request() {
    const CASE: &str = "ADVA_SERIALIZED_LEAF_CONSUMER_CASE";
    const REQUEST_PATH: &str = "ADVA_SERIALIZED_LEAF_REQUEST_PATH";

    let case = std::env::var(CASE).expect("consumer case must be supplied");
    let request_path = std::env::var(REQUEST_PATH).expect("request path must be supplied");
    producer::receive_pinned_serialized_leaf_request(
        &case,
        std::path::Path::new(&request_path),
    );
}
