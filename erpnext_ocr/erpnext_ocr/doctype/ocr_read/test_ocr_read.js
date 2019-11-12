/* eslint-disable */
// rename this file from _test_[name] to test_[name] to activate
// and remove above this line

QUnit.test("test: OCR Read", function (assert) {
	let done = assert.async();

	// number of asserts
	assert.expect(1);

	frappe.run_serially([
		// insert a new OCR Read
		() => frappe.tests.make('OCR Read', [
			// values to be set
			{language: 'en'}
		]),
		() => {
			assert.equal(cur_frm.doc.language, 'en');
		},
		() => done()
	]);

});
