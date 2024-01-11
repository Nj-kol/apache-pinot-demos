## Processing Semantics

There there three categories of processing guarantees each with their own set of tradeoff 
- At-most-once—A message may get lost, but it will never be processed a second time.
- At-least-once—A message will never be lost, but it may be processed more than once.
- Exactly-once—A message is never lost and will be processed only once.
#### At-most-once
- At-most-once is the simplest delivery guarantee a system can offer; no special logic is required anywhere.
- In essence, if a message gets dropped, a stream processor crashes, or the machine that a stream processor is running on fails, the message is lost. This is essentially a ***fire-and-forget* model
#### At-least-once
- At-least-once increases the complexity because the streaming system must keep track of every message that was sent to the stream processor and an acknowledgment that it was received. 
- If the streaming manager determines that the message wasn’t processed (perhaps it was lost or the stream processor didn’t respond within a given time boundary), then it will be re-sent. 
- At this level of messaging guarantee, ***your streaming job may be sent the same message multiple times***. ***Therefore your streaming job must be idempotent,*** meaning that every time your streaming job receives the same message, it produces the same result.  If you remember this when designing your streaming jobs, you’ll be able to handle the duplicate-messages situation
#### Exactly-once
- Exactly-once semantics ratchets up the complexity a little more for the stream processing framework. Besides the bookkeeping that it must keep for all messages that have been sent, now it must also detect and ignore duplicates.
-  With this level of guarantee your streaming job no longer has to worry about dealing with duplicate messages—it only has to make sure it responds with a success or failure after a message is processed.
### Which guarantee to choose

You may be wondering which of these guarantees you need; it depends on the business problem you’re trying to solve.
#### Case 1: Turbine engine monitoring system

Say we want to constantly analyze how our turbine engine is performing so we can predict when a failure may occur and preemptively perform maintenance. Turbines produce approximately 1 TB of data every hour—keep in mind that’s one turbine, and we’re monitoring thousands to be able to predict when a failure may occur.  

Do we need to ensure we don’t lose a single message? We may, but it would be worth investigating whether our prediction algorithm needs all the data. If it can perform adequately with data missing, then I’d choose the least complex guarantee first and work from there.
#### Case 2 : Financial Transactions

What if instead your business problem involved making a financial transaction based on a streaming query? Perhaps you operate an ad network and you provide real-time billing to your clients. In this case you’d want to ensure that the streaming system. You choose provides exactly-once semantics. 
## State Management

Once your streaming analysis algorithm becomes more complicated than using the current message without dependencies on any previous messages and/or external data, you’ll need to maintain state and will likely need the state management services provided by your framework of choice

![](state_management_1.jpg)

Fromt he figure, it should be obvious where you need to keep state—right there in the stream processor where your job performs the counting by user ID

The state management facilities provided by various systems naturally fall along a complexity continuum :

![](state_management_2.jpg)

The continuum starts on the left with a naïve in-memory-only choice,, and progresses to the other end of the spectrum with systems that provide ***a queryable persistent state*** that’s replicated.

For Example, Spark Streaming uses ***RocksDB*** as a state store.

With frameworks implementing the later,  you can join together different streams of data. Imagine you were running an ad-serving business and you wanted to track two things: the ad impression and the ad click. It’s reasonable that the collection of this data would result in two streams of data, one for ad impressions and one for ad clicks.  Figure shows how these streams and your streaming job would be set up for handling this.

![](state_management_3.jpg)
## Fault Tolerance

A stream-processing framework’s ability to keep going in the face of failures is a direct result of its fault-tolerance capabilities. When you consider all the pieces involved in stream processing, there are quite a few places where it can fail.

![](fault_tolerance.jpg)

If we take the list and consolidate it down to the common elements, we end up with the following:
- **Data loss**—This covers data lost on the network and also the stream processor or your job crashing and losing data that was in memory during the crash
- **Loss of resource management**—This covers the streaming manager and your application driver, in the event you have one.
### Fault Tolerance mechanisms

When it comes to stream-processing frameworks, all the common techniques for dealing with failures involve some variant of replication and coordination. 

In general there are two common approaches a streaming system may take toward replication and coordination.  
1. State-machine
2. Rollback recovery
#### State Machine 
- The first approach used by stream-processing systems is known as state-machine. 
- With this approach the stream manager replicates the streaming job on independent nodes and coordinates the replicas by sending the same input in the same order to all.
- In Spark, for example, this is called ***Speculative Execution***
#### Rollback recovery ( Checkpointing )
- The second approach is known as rollback recovery.
- In this approach the stream processor periodically packages the state of our computation into what is called a checkpoint, which it copies to a different stream processor node or a nonvolatile location such as a disk.
