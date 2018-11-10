
import smart_imports

smart_imports.all()


class CheckUserLogicTests(utils_testcase.TestCase):

    def setUp(self):
        super(CheckUserLogicTests, self).setUp()
        self.user_email = 'test@mailinator.com'
        self.check_user_md5 = logic.check_user_md5(command=relations.COMMAND_TYPE.CHECK, v1=self.user_email)

    def test_check_user_md5(self):
        self.assertEqual(self.check_user_md5, '547855941988ea3a567e9b6b9d0ab6fb')

    def test_check_user__wrong_md5(self):
        self.assertTrue(logic.check_user(command=relations.COMMAND_TYPE.CHECK,
                                         external_md5='bla-bla',
                                         v1=self.user_email,
                                         v2=None,
                                         v3=None).is_WRONG_MD5)

    def test_check_user__no_v1(self):
        self.assertTrue(logic.check_user(command=relations.COMMAND_TYPE.CHECK,
                                         external_md5=self.check_user_md5,
                                         v1=None,
                                         v2=None,
                                         v3=None).is_NOT_SPECIFIED_V1)

    def test_check_user__user_exists(self):
        with mock.patch('the_tale.finances.bank.logic.get_account_id', mock.Mock(return_value=13)) as bank_check_user:
            self.assertTrue(logic.check_user(command=relations.COMMAND_TYPE.CHECK,
                                             external_md5=self.check_user_md5,
                                             v1=self.user_email,
                                             v2=None,
                                             v3=None).is_USER_EXISTS)

        self.assertEqual(bank_check_user.call_count, 1)
        self.assertEqual(bank_check_user.call_args, mock.call(email=self.user_email))

    def test_check_user__user_not_exists(self):
        with mock.patch('the_tale.finances.bank.logic.get_account_id', mock.Mock(return_value=None)) as bank_check_user:
            self.assertTrue(logic.check_user(command=relations.COMMAND_TYPE.CHECK,
                                             external_md5=self.check_user_md5,
                                             v1=self.user_email,
                                             v2=None,
                                             v3=None).is_USER_NOT_EXISTS)

        self.assertEqual(bank_check_user.call_count, 1)
        self.assertEqual(bank_check_user.call_args, mock.call(email=self.user_email))


class PayLogicTests(utils_testcase.TestCase):

    def setUp(self):
        super(PayLogicTests, self).setUp()
        self.user_email = 'test@mailinator.com'
        self.xsolla_id = '666'
        self.payment_sum = '13'
        self.pay_md5 = logic.pay_md5(command=relations.COMMAND_TYPE.PAY, v1=self.user_email, id=self.xsolla_id)

    def test_pay__md5(self):
        self.assertEqual(self.pay_md5, '5be626d4d109cb65ba36d6752bbb772e')

    def test_pay__wrong_md5(self):
        self.assertTrue(logic.pay(command=relations.COMMAND_TYPE.PAY,
                                  external_md5=None,
                                  v1=self.user_email, v2=None, v3=None,
                                  id=self.xsolla_id, sum=self.payment_sum, test=False, date=None, request_url='bla-bla.test.com'),
                        (relations.PAY_RESULT.WRONG_MD5, None))
        self.assertTrue(logic.pay(command=relations.COMMAND_TYPE.PAY,
                                  external_md5='weadadsasdasd',
                                  v1=self.user_email, v2=None, v3=None,
                                  id=self.xsolla_id, sum=self.payment_sum, test=False, date=None, request_url='bla-bla.test.com'),
                        (relations.PAY_RESULT.WRONG_MD5, None))

    def test_pay__no_v1(self):
        self.assertTrue(logic.pay(command=relations.COMMAND_TYPE.PAY,
                                  external_md5=self.pay_md5,
                                  v1=None, v2=None, v3=None,
                                  id=self.xsolla_id, sum=self.payment_sum, test=False, date=None, request_url='bla-bla.test.com'),
                        (relations.PAY_RESULT.NOT_SPECIFIED_V1, None))

    def test_pay__no_id(self):
        self.assertTrue(logic.pay(command=relations.COMMAND_TYPE.PAY,
                                  external_md5=self.pay_md5,
                                  v1=self.user_email, v2=None, v3=None,
                                  id=None, sum=self.payment_sum, test=False, date=None, request_url='bla-bla.test.com'),
                        (relations.PAY_RESULT.NOT_SPECIFIED_ID, None))

    def test_pay__no_sum(self):
        self.assertTrue(logic.pay(command=relations.COMMAND_TYPE.PAY,
                                  external_md5=self.pay_md5,
                                  v1=self.user_email, v2=None, v3=None,
                                  id=self.xsolla_id, sum=None, test=False, date=None, request_url='bla-bla.test.com'),
                        (relations.PAY_RESULT.NOT_SPECIFIED_SUM, None))

    def test_pay__success(self):
        self.assertEqual(prototypes.InvoicePrototype._db_count(), 0)
        with mock.patch('the_tale.finances.bank.logic.get_account_id', mock.Mock(return_value=1234)):
            result, invoice_id = logic.pay(command=relations.COMMAND_TYPE.PAY,
                                           external_md5=self.pay_md5,
                                           v1=self.user_email, v2=None, v3=None,
                                           id=self.xsolla_id, sum=self.payment_sum, test=False, date=None, request_url='bla-bla.test.com')

        self.assertTrue(result.is_SUCCESS)
        self.assertNotEqual(invoice_id, None)
        self.assertTrue(isinstance(invoice_id, int))
        self.assertEqual(prototypes.InvoicePrototype._db_count(), 1)

    def test_test_is_none(self):
        self.assertEqual(prototypes.InvoicePrototype._db_count(), 0)
        with mock.patch('the_tale.finances.bank.logic.get_account_id', mock.Mock(return_value=1234)):
            result, invoice_id = logic.pay(command=relations.COMMAND_TYPE.PAY,
                                           external_md5=self.pay_md5,
                                           v1=self.user_email, v2=None, v3=None,
                                           id=self.xsolla_id, sum=self.payment_sum, test=None, date=None, request_url='bla-bla.test.com')

        self.assertTrue(result.is_SUCCESS)
        self.assertEqual(prototypes.InvoicePrototype._db_count(), 1)
        self.assertFalse(prototypes.InvoicePrototype._db_get_object(0).test)

    def test_test_is_0(self):
        self.assertEqual(prototypes.InvoicePrototype._db_count(), 0)
        with mock.patch('the_tale.finances.bank.logic.get_account_id', mock.Mock(return_value=1234)):
            result, invoice_id = logic.pay(command=relations.COMMAND_TYPE.PAY,
                                           external_md5=self.pay_md5,
                                           v1=self.user_email, v2=None, v3=None,
                                           id=self.xsolla_id, sum=self.payment_sum, test='0', date=None, request_url='bla-bla.test.com')

        self.assertTrue(result.is_SUCCESS)
        self.assertEqual(prototypes.InvoicePrototype._db_count(), 1)
        self.assertFalse(prototypes.InvoicePrototype._db_get_object(0).test)

    def test_test_is_1(self):
        self.assertEqual(prototypes.InvoicePrototype._db_count(), 0)
        with mock.patch('the_tale.finances.bank.logic.get_account_id', mock.Mock(return_value=1234)):
            result, invoice_id = logic.pay(command=relations.COMMAND_TYPE.PAY,
                                           external_md5=self.pay_md5,
                                           v1=self.user_email, v2=None, v3=None,
                                           id=self.xsolla_id, sum=self.payment_sum, test='1', date=None, request_url='bla-bla.test.com')

        self.assertTrue(result.is_SUCCESS)
        self.assertEqual(prototypes.InvoicePrototype._db_count(), 1)
        self.assertTrue(prototypes.InvoicePrototype._db_get_object(0).test)


class CancelLogicTests(utils_testcase.TestCase):

    def setUp(self):
        super(CancelLogicTests, self).setUp()
        self.xsolla_id = '666'
        self.cancel_md5 = logic.cancel_md5(command=relations.COMMAND_TYPE.CANCEL, id=self.xsolla_id)

    def test_cancel_md5(self):
        self.assertEqual(self.cancel_md5, '4325a08965b49c34f492865c0c4d76f9')
