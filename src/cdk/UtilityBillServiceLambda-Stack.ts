
import { Construct } from 'constructs';
import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import { execSync } from 'child_process';
import { IFunction } from "aws-cdk-lib/aws-lambda";
import { Rule, Schedule } from 'aws-cdk-lib/aws-events';
import { Queue } from 'aws-cdk-lib/aws-sqs';
import { LambdaFunction } from 'aws-cdk-lib/aws-events-targets';
// import { StringParameter } from 'aws-cdk-lib/aws-ssm';

import lambda = require('aws-cdk-lib/aws-lambda');
import { Effect, Policy, PolicyStatement } from 'aws-cdk-lib/aws-iam';


export class UtilityBillLambdaStack extends Stack {
  public readonly lambdaFunction: IFunction;
  public readonly scheduleRule: Rule;


  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);


    // --- lambda function
    this.lambdaFunction = new lambda.Function(this, 'UtilityBillServiceLambda', {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'main.handler',
      code: lambda.Code.fromAsset('./src/lambda', {
        bundling: {
          image: lambda.Runtime.PYTHON_3_9.bundlingImage,
          command: [],
          local: {
            tryBundle(outputDir: string) {
              try {
                execSync('pip3 --version');
              } catch {
                return false;
              }

              const commands = [
                `cd src/lambda`,
                `pip3 install -r requirements.txt -t ${outputDir}`,
                `cp -a . ${outputDir}`
              ];

              execSync(commands.join(' && '));
              return true;
            }
          }
        }
      }),
      memorySize: 1024,
      // functionName: 'UtilityBillLambda', // We do NOT specify a name so that replacements work.
      timeout: Duration.seconds(300),
      // environment: {
      //   "GOOGLE_CREDENTIALS_PARAMETER": StringParameter.valueFromLookup(this, "UtilityBillService-GoogleDriveServiceAccount")
      // }
    });


    // --- eventbridge Rule for continual trigger
    this.scheduleRule = new Rule(this, "UtilityBillServiceSchedulerRule", {
      // ruleName: "UtilityBillServiceSchedulerRule",
      description: "Runs the UtilityBillServiceLambda twice a month. On the 1st and 20th of every month, at 6pm",
      schedule: Schedule.cron({
        minute: '0',
        hour: '18',
        month: '*',
        day:'1,20',
        year: '*'
      }),
    });

    // --- binding eventbridge rule to lambda and adding DLQ
    this.scheduleRule.addTarget(new LambdaFunction(this.lambdaFunction, {
      deadLetterQueue: new Queue(this, "UtilityBillServiceSchedulerDLQ"), // Optional: add a dead letter queue
      retryAttempts: 2, // Optional: set the max number of retry attempts
    }));

    // -- give lambda access to SSM
    this.lambdaFunction.role?.attachInlinePolicy(
      new Policy(this, "SSM Policy", {
        statements: [
          new PolicyStatement({
            effect: Effect.ALLOW,
            actions: [
              "ssm:Describe*",
              "ssm:Get*",
              "ssm:List*"
            ],
            resources: ["*"]
          }),
        ],
      }),
    );

  }
}
